import React, { useState, useEffect } from "react";
import "../styles/Category.css";
import axios from "axios";
import { getAuth, onAuthStateChanged } from "firebase/auth";
import { Helmet } from "react-helmet";

function Category() {
  const [categories, setCategories] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [selectedMonth, setSelectedMonth] = useState(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
  });

  // IMPORTANT FIX: userId starts as null, not empty string
  const [userId, setUserId] = useState(null);

  // 🚀 Firebase Auth Listener
  useEffect(() => {
    const auth = getAuth();
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUserId(user ? user.uid : "");
    });
    return () => unsubscribe();
  }, []);

  // SHOW loading screen while Firebase is checking auth

 useEffect(() => {
    const fetchCategories = async () => {
      if (!userId) return; // skip if not logged in

      try {
        setLoading(true);
        setError(null);

        const response = await axios.get(
          `https://expn-backend.onrender.com/get_categories?uid=${userId}&month=${selectedMonth}`
        );

        setCategories(response.data || {});
      } catch (err) {
        console.error("Error fetching categories:", err);
        setError("Failed to fetch categories");
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, [userId, selectedMonth]);
  const formatCurrency = (amount) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: "INR" }).format(amount);

  const formatDate = (timestamp) =>
    new Date(timestamp).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });

  // ⭐ Fetch categories AFTER userId is ready
   if (userId === null) {
    return <p className="loading">Checking login...</p>;
  }

  if (loading) return <p className="loading">Loading categories...</p>;
  if (error) return <p className="error">{error}</p>;

  // Calculate month's total
  const totalForMonth = Object.values(categories).reduce(
    (sum, cat) => sum + (cat.total || 0),
    0
  );

  return (
    <>
      <Helmet>
        <link rel="icon" type="/image/png" href="logo.png" />
        <title>Categories • Expn</title>
      </Helmet>

      <div className="category-dashboard">
        <div className="dashboard-header">
          <h1>Spending Overview</h1>
          <p>Overview of your spending by category</p>

          <div className="month-selector">
            <label htmlFor="month">Select Month: </label>
            <input
              type="month"
              id="month"
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(e.target.value)}
            />
          </div>
        </div>

        {/* Total Card */}
        <div className="total-card">
          <h2>Total Spending</h2>
          <p className="total-value">{formatCurrency(totalForMonth)}</p>
          <p className="total-month">
            for{" "}
            {new Date(selectedMonth).toLocaleString("en-US", {
              month: "long",
              year: "numeric",
            })}
          </p>
        </div>

        <div className="categories-grid">
          {Object.entries(categories)
            .filter(([_, cat]) => (cat.total || 0) > 0)
            .map(([name, cat]) => (
              <div key={name} className="category-card">
                <div className="card-header">
                  <h2 className="category-name">{name}</h2>
                  <span className="total-amount">{formatCurrency(cat.total)}</span>
                </div>

                <div className="transactions-section">
                  <h3>Transactions</h3>
                  <ul className="scrollable">
                    {cat.transactions?.length > 0 ? (
                      cat.transactions.map((t, idx) => (
                        <li key={idx} className="transaction-item">
                          <span className="transaction-date">{formatDate(t.timestamp)}</span>
                          <span className="transaction-name">{t.name}</span>
                          {t.merchant && (
                            <span className="transaction-merchant">{t.merchant}</span>
                          )}
                          <span className="transaction-amount">
                            {formatCurrency(t.expense)}
                          </span>
                        </li>
                      ))
                    ) : (
                      <li className="no-transactions">No transactions</li>
                    )}
                  </ul>
                </div>
              </div>
            ))}

          {Object.keys(categories).length === 0 && (
            <div className="empty-state">
              <h3>No categories found</h3>
              <p>Add expenses to see category breakdowns.</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default Category;

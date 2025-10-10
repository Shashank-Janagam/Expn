import React, { useState, useEffect } from "react";
import "../styles/Category.css";
import axios from "axios";
import { getAuth, onAuthStateChanged } from "firebase/auth";

function Category() {
  const [categories, setCategories] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [selectedMonth, setSelectedMonth] = useState(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
  });

  const [userId, setUserId] = useState("");  

  useEffect(() => {
    const auth = getAuth();
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) setUserId(user.uid);
      else setUserId("");
    });
    return () => unsubscribe();
  }, []);

  const formatCurrency = (amount) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: "INR" }).format(amount);

  const formatDate = (timestamp) =>
    new Date(timestamp).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });

  // Refetch whenever userId or selectedMonth changes
  useEffect(() => {
    const fetchCategories = async () => {
      if (!userId) return;
      try {
        setLoading(true);
        setError(null);

        const response = await axios.get(
          `http://127.0.0.1:5000/get_categories?uid=${userId}&month=${selectedMonth}`
        );

        setCategories(response.data);
      } catch (err) {
        console.error("Error fetching categories:", err);
        setError("Failed to fetch categories");
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, [userId, selectedMonth]); // ✅ Add selectedMonth here

  if (loading) return <p className="loading">Loading categories...</p>;
  if (error) return <p className="error">{error}</p>;

  return (
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

      <div className="categories-grid">
        {Object.entries(categories)
            .filter(([_, categoryData]) => categoryData.total > 0) // ✅ skip zero totals
            .map(([categoryName, categoryData]) => (
              <div key={categoryName} className="category-card">
                <div className="card-header">
                  <h2 className="category-name">{categoryName}</h2>
                  <span className="total-amount">{formatCurrency(categoryData.total)}</span>
            </div>

            <div className="transactions-section">
              <h3>Transactions</h3>
              <ul className="scrollable">
                {categoryData.transactions && categoryData.transactions.length > 0 ? (
                  categoryData.transactions.map((t, idx) => (
                    <li key={idx} className="transaction-item">
                      <span className="transaction-name">{t.name}</span>
                      {t.merchant && <span className="transaction-merchant">{t.merchant}</span>}
                      <span className="transaction-date">{formatDate(t.timestamp)}</span>
                      <span className="transaction-amount">{formatCurrency(t.expense)}</span>
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
  );
}

export default Category;

import React, { useState ,useEffect} from 'react';
import { User, DollarSign, BarChart2, List, PlusCircle } from 'lucide-react';
import '../styles/Home.css';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { getAuth, onAuthStateChanged } from "firebase/auth";

function Dashboard() {
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const [expenseInput, setExpenseInput] = useState('');
  const navigate = useNavigate();

  const [totalExp,setTotalExp]=useState(0);
const [userId, setUserId] = useState("");  // ✅

useEffect(() => {
  if (!userId) return;

  const fetchMonthlyTotal = async () => {
    try {
      const currentMonth = new Date().toISOString().slice(0, 7); // "YYYY-MM"
      const res = await axios.get(
        `https://expn-backend.onrender.com/get_user_month_total?uid=${userId}&month=${currentMonth}`
      );
      setTotalExp(res.data.total || 0);
    } catch (err) {
      console.error("Error fetching monthly total:", err);
    }
  };

  fetchMonthlyTotal();
}, [userId]);

  



useEffect(() => {
  const auth = getAuth();
  const unsubscribe = onAuthStateChanged(auth, (user) => {
    if (user) {
      setUserId(user.uid);  // ✅ set Firebase UID
    } else {
      setUserId("");
    }
  });

  return () => unsubscribe();
}, []);

console.log("User ID in Dashboard:", userId);
  const navigateToProfile = () => {
    setIsProfileMenuOpen(false);
  };

  const handleLogout = () => {
    localStorage.removeItem("uid");
    navigate('/');
    console.log("Logging out...");
    // Add logout logic
  };

  const handleExpenseSubmit = async (e) => {
    e.preventDefault();
    if (!expenseInput.trim()) return;
    console.log("New expense added:", expenseInput);
    const text=expenseInput;
    setExpenseInput("");
    try{
      axios.post("https://expn-backend.onrender.com/add_expense",{
        text:text,
        uid:userId,
        timeStamp:new Date().toISOString()
      });

      setExpenseInput("");
    }catch(err){
      console.error("Error adding expense:", err);
    }


    setExpenseInput('');
  };
  const goToCategories = () => {
    navigate("/Category",{state:{ userId }});
  };
  return (
    

    <div className="home-container">

          <div className="dashboard-container">
      

    </div>
      {/* Header */}
      <header className="header">
        {/* Logo */}
        <div className="logo-container">
          <div className="logo-icon">
            <span className="logo-text">Expn   </span>
          </div>
        </div>

        {/* Profile */}
        <div className="profile-wrapper">
          <button
            className="profile-button"
            onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
          >
            <User className="profile-icon" />
          </button>

          {isProfileMenuOpen && (
            <div className="profile-dropdown">
              <button onClick={navigateToProfile} className="profile-dropdown-item">
                View Profile
              </button>
              <button className="profile-dropdown-item">Settings</button>
              <div className="profile-dropdown-separator">
                <button className="profile-dropdown-item" onClick={handleLogout}>
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Dashboard Content */}
      <main className="main-content">
        <div className="hero-container">
<div className="hero-text-container">
  <div className="hero-title-wrapper">
    <DollarSign className="hero-icon" />
    <h1 className="hero-title">Expn</h1>
  </div>
  <p className="hero-subtitle">
    Track your spending, analyze budgets, and manage your financial goals.
  </p>

  {/* Move button here */}
  <button 
    onClick={goToCategories} 
    className="navigate-button"
  >
    View Spending
  </button>
</div>


          

          {/* Manual Expense Entry */}
          <form onSubmit={handleExpenseSubmit} className="search-form">
            <div className="search-wrapper">
              <input
                type="text"
                value={expenseInput}
                onChange={(e) => setExpenseInput(e.target.value)}
                placeholder="Spent 750 for yesterday's lunch.."
                className="search-input"
              />
              <button type="submit" className="search-submit" disabled={!expenseInput.trim()}>
                <PlusCircle className="search-icon" />
              </button>
            </div>
          </form>

          {/* Dashboard Widgets */}
          <div className="dashboard-widgets" style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
            gap: "1.5rem",
            marginTop: "2rem"
          }}>
          <div className="widget-card">
            <BarChart2 className="hero-icon" />
            <h3>Total Expenses</h3>
            <p>₹ {totalExp.toLocaleString()}</p>
          </div>


            <div className="widget-card">
              <List className="hero-icon" />
              <h3>Recent Transactions</h3>
              <p>5 new this week</p>
            </div>

            <div className="widget-card">
              <DollarSign className="hero-icon" />
              <h3>Monthly Budget</h3>
              <p>75% used</p>
            </div>





          </div>
        </div>
      </main>
    </div>
  );
}

export default Dashboard;

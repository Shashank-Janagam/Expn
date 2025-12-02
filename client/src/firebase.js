// firebase.js
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyBwiwTrAxN93hyxYkaSzJhc7mvI1vghHB0",
  authDomain: "expn-a06bb.firebaseapp.com",
  projectId: "expn-a06bb",
  storageBucket: "expn-a06bb.firebasestorage.app",
  messagingSenderId: "647422054275",
  appId: "1:647422054275:web:58817538d47c4eb118f0b6",
  measurementId: "G-EF7NFW8TKN"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

export { auth, provider };

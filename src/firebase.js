// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBo3iMfjPLo7OaIMwvW1N5Iv9Yl4tKBH68",
  authDomain: "newhacks-b1349.firebaseapp.com",
  projectId: "newhacks-b1349",
  storageBucket: "newhacks-b1349.firebasestorage.app",
  messagingSenderId: "1085816255113",
  appId: "1:1085816255113:web:c4e77af2826a632a070c58",
  measurementId: "G-RZV307TSSM"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
export const auth = getAuth(app);
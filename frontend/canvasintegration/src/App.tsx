import React from 'react';
import './index.css'; 
import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './components/HomePage';

const App: React.FC = () => {
  return (
    <div className="app-container">
      <Header />
      <main className="container mt-4">
        <HomePage />
      </main>
      <Footer />
    </div>
  );
};

export default App;

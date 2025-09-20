import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import CarList from './pages/CarList';
import CarDetail from './pages/CarDetail';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<CarList />} />
          <Route path="/cars/:id" element={<CarDetail />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

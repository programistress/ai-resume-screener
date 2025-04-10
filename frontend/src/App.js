import './App.css'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import WelcomePage from './pages/WelcomePage';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<WelcomePage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

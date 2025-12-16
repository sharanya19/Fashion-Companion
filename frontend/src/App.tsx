import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Wardrobe from './pages/Wardrobe';
import Stylist from './pages/Stylist';
import Chat from './pages/Chat';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Dashboard />} />
          <Route path="/wardrobe" element={<Wardrobe />} />
          <Route path="/stylist" element={<Stylist />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;

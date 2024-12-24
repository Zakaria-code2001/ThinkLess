import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import TodoPage from './pages/TodoPage';
import NotesPage from './pages/NotesPage';

const App = () => {
  return (
    <Router>
      <div className="flex">
        <Sidebar />
        <div className="flex-1">
          <Routes>
            <Route path="/todos" element={<TodoPage />} />
            <Route path="/notes" element={<NotesPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
};

export default App;

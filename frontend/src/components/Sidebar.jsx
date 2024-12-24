import React from 'react';
import { Link } from 'react-router-dom';

const Sidebar = () => {
  return (
    <div className="w-64 h-screen bg-gray-800 text-white flex flex-col">
      <h2 className="text-xl font-bold p-4">ThinkLess App</h2>
      <nav className="flex-1">
        <ul>
          <li className="p-4 hover:bg-gray-700">
            <Link to="/todos">Todo Service</Link>
          </li>
          <li className="p-4 hover:bg-gray-700">
            <Link to="/notes">Notes Service</Link>
          </li>
        </ul>
      </nav>
    </div>
  );
};

export default Sidebar;

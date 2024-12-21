import React, { useState, useEffect } from "react";
import { getTodos, addTodo, deleteTodo } from "./services/todoService";

function App() {
  const [todos, setTodos] = useState([]);
  const [newTodo, setNewTodo] = useState("");
  const [showTodos, setShowTodos] = useState(false);  // State for showing/hiding the todo list

  useEffect(() => {
    const fetchTodos = async () => {
      try {
        const todosData = await getTodos();
        setTodos(todosData);
      } catch (error) {
        console.error("Error fetching todos:", error);
      }
    };

    fetchTodos();
  }, []);

  const handleAddTodo = async () => {
    const todo = { title: newTodo, description: "", completed: false };
    try {
      const addedTodo = await addTodo(todo);
      setTodos([...todos, addedTodo]);
      setNewTodo(""); // Reset input
    } catch (error) {
      console.error("Error adding todo:", error);
    }
  };

  const handleDeleteTodo = async (todoId) => {
    try {
      await deleteTodo(todoId);
      setTodos(todos.filter((todo) => todo.id !== todoId));
    } catch (error) {
      console.error("Error deleting todo:", error);
    }
  };

  const toggleTodoVisibility = () => {
    setShowTodos((prevState) => !prevState);  // Toggle the visibility
  };

  return (
    <div className="App">
      <h1>Todo List</h1>
      
      {/* Input for new todo */}
      <div>
        <input
          type="text"
          value={newTodo}
          onChange={(e) => setNewTodo(e.target.value)}
        />
        <button onClick={handleAddTodo}>Add Todo</button>
      </div>

      {/* Button to toggle the visibility of the todo list */}
      <button onClick={toggleTodoVisibility}>
        {showTodos ? "Hide Todo List" : "Show Todo List"}
      </button>

      {/* Conditionally render the todo list based on showTodos state */}
      {showTodos && (
        <ul>
          {todos.map((todo) => (
            <li key={todo.id}>
              {todo.title} - {todo.completed ? "Completed" : "Not Completed"}
              <button onClick={() => handleDeleteTodo(todo.id)}>Delete</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;

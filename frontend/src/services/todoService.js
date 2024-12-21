// src/services/todoService.js

const API_URL = "http://127.0.0.1:8000/api/v1/todos"; // Update with your FastAPI endpoint

// Fetch all todos
export const getTodos = async () => {
  const response = await fetch(API_URL);
  if (!response.ok) {
    throw new Error('Error fetching todos');
  }
  return await response.json();
};

// Add a new todo
export const addTodo = async (todo) => {
  const response = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(todo),
  });

  if (!response.ok) {
    throw new Error('Error adding todo');
  }

  return await response.json();
};

// Delete a todo by ID
export const deleteTodo = async (todoId) => {
  const response = await fetch(`${API_URL}/${todoId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error('Error deleting todo');
  }

  return await response.json();
};

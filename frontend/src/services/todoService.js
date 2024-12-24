// src/services/todoService.js
import axiosInstance from '../api/axios';

export const fetchTodos = async () => {
  try {
    const response = await axiosInstance.get('todos');
    return response.data;
  } catch (error) {
    console.error('Error fetching todos:', error);
    throw error;
  }
};

export const createTodo = async (todoData) => {
  try {
    const response = await axiosInstance.post('todos', todoData);
    return response.data;
  } catch (error) {
    console.error('Error creating todo:', error);
    throw error;
  }
};

// Add other CRUD operations (update, delete) here as needed

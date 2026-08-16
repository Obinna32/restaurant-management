import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/menu';

export const fetchCategories = async () => {
  const response = await axios.get(`${API_BASE_URL}/categories/`);
  return response.data;
};

export const fetchMenuItems = async (categoryId = null) => {
  let url = `${API_BASE_URL}/items/?available=true`;
  if (categoryId) {
    url += `&category=${categoryId}`;
  }
  const response = await axios.get(url);
  return response.data;
};
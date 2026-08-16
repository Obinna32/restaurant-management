import React, { useState, useEffect } from 'react';
import { fetchCategories, fetchMenuItems } from '../services/menuApi';

const Menu = () => {
  const [categories, setCategories] = useState([]);
  const [menuItems, setMenuItems] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCategories();
    loadMenuItems();
  }, []);

  const loadCategories = async () => {
    try {
      const data = await fetchCategories();
      setCategories(data);
    } catch (err) {
      console.error('Failed to load categories:', err);
    }
  };

  const loadMenuItems = async (categoryId = null) => {
    setLoading(true);
    try {
      const data = await fetchMenuItems(categoryId);
      setMenuItems(data);
    } catch (err) {
      console.error('Failed to load menu items:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCategorySelect = (categoryId) => {
    setSelectedCategory(categoryId);
    loadMenuItems(categoryId);
  };

  const filteredItems = menuItems.filter((item) =>
    item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (item.description && item.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Our Menu</h1>
        <p className="mt-2 text-lg text-gray-600">Explore our delicious selection prepared fresh daily.</p>
      </div>

      {/* Search Bar */}
      <div className="max-w-md mx-auto mb-8">
        <input
          type="text"
          placeholder="Search dishes..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:outline-none"
        />
      </div>

      {/* Category Tabs */}
      <div className="flex justify-center flex-wrap gap-2 mb-8">
        <button
          onClick={() => handleCategorySelect(null)}
          className={`px-4 py-2 rounded-full font-medium transition-colors ${
            selectedCategory === null
              ? 'bg-amber-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All Items
        </button>
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => handleCategorySelect(cat.id)}
            className={`px-4 py-2 rounded-full font-medium transition-colors ${
              selectedCategory === cat.id
                ? 'bg-amber-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {cat.name}
          </button>
        ))}
      </div>

      {/* Menu Grid */}
      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading delicious items...</div>
      ) : filteredItems.length === 0 ? (
        <div className="text-center py-12 text-gray-500">No menu items found.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredItems.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow border border-gray-100 flex flex-col justify-between"
            >
              <div>
                {item.image_url && (
                  <img
                    src={item.image_url}
                    alt={item.name}
                    className="w-full h-48 object-cover"
                  />
                )}
                <div className="p-5">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-xl font-bold text-gray-900">{item.name}</h3>
                    <span className="bg-amber-100 text-amber-800 text-sm font-bold px-3 py-1 rounded-full">
                      N{parseFloat(item.price).toFixed(2)}
                    </span>
                  </div>
                  <p className="text-gray-600 text-sm line-clamp-2">
                    {item.description || 'No description available.'}
                  </p>
                </div>
              </div>
              <div className="p-5 pt-0 flex justify-between items-center text-xs text-gray-500">
                <span>⏱️ {item.preparation_time_minutes} mins prep</span>
                <span className="capitalize text-amber-700 font-medium">
                  {item.category_name}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Menu;
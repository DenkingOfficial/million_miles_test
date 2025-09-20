import React, { useState, useEffect } from 'react';
import { carService } from '../services/api';
import './Filters.css';

const Filters = ({ onFiltersChange, currentFilters }) => {
  const [filterOptions, setFilterOptions] = useState({
    manufacturers: [],
    fuel_types: [],
    transmissions: [],
    cities: [],
    price_range: { min: 0, max: 10000 },
    year_range: { min: 2000, max: 2025 }
  });

  const [localFilters, setLocalFilters] = useState(currentFilters);

  useEffect(() => {
    loadFilterOptions();
  }, []);

  const loadFilterOptions = async () => {
    try {
      const options = await carService.getFilterOptions();
      setFilterOptions(options);
    } catch (error) {
      console.error('Failed to load filter options:', error);
    }
  };

  const handleFilterChange = (key, value) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const clearFilters = () => {
    const emptyFilters = {};
    setLocalFilters(emptyFilters);
    onFiltersChange(emptyFilters);
  };

  return (
    <div className="filters">
      <div className="filters-header">
        <h3>Фильтры</h3>
        <button onClick={clearFilters} className="clear-filters">
          Очистить
        </button>
      </div>

      <div className="filter-group">
        <label>Производитель</label>
        <select
          value={localFilters.manufacturer || ''}
          onChange={(e) => handleFilterChange('manufacturer', e.target.value || undefined)}
        >
          <option value="">Все бренды</option>
          {filterOptions.manufacturers.map(manufacturer => (
            <option key={manufacturer} value={manufacturer}>
              {manufacturer}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Тип двигателя</label>
        <select
          value={localFilters.fuel_type || ''}
          onChange={(e) => handleFilterChange('fuel_type', e.target.value || undefined)}
        >
          <option value="">Все типы</option>
          {filterOptions.fuel_types.map(fuel => (
            <option key={fuel} value={fuel}>
              {fuel}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Трансмиссия</label>
        <select
          value={localFilters.transmission || ''}
          onChange={(e) => handleFilterChange('transmission', e.target.value || undefined)}
        >
          <option value="">Все типы</option>
          {filterOptions.transmissions.map(transmission => (
            <option key={transmission} value={transmission}>
              {transmission}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Город</label>
        <select
          value={localFilters.office_city_state || ''}
          onChange={(e) => handleFilterChange('office_city_state', e.target.value || undefined)}
        >
          <option value="">Все города</option>
          {filterOptions.cities.map(city => (
            <option key={city} value={city}>
              {city}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Диапазон цен</label>
        <div className="range-inputs">
          <input
            type="number"
            placeholder="От"
            value={localFilters.min_price || ''}
            onChange={(e) => handleFilterChange('min_price', e.target.value ? Number(e.target.value) : undefined)}
          />
          <span>-</span>
          <input
            type="number"
            placeholder="До"
            value={localFilters.max_price || ''}
            onChange={(e) => handleFilterChange('max_price', e.target.value ? Number(e.target.value) : undefined)}
          />
        </div>
      </div>

      <div className="filter-group">
        <label>Год производства</label>
        <div className="range-inputs">
          <input
            type="number"
            placeholder="От"
            value={localFilters.min_year || ''}
            onChange={(e) => handleFilterChange('min_year', e.target.value ? Number(e.target.value) : undefined)}
          />
          <span>-</span>
          <input
            type="number"
            placeholder="До"
            value={localFilters.max_year || ''}
            onChange={(e) => handleFilterChange('max_year', e.target.value ? Number(e.target.value) : undefined)}
          />
        </div>
      </div>
    </div>
  );
};

export default Filters;

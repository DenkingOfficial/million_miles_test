import React from 'react';
import './SortControls.css';

const SortControls = ({ onSortChange, currentSort }) => {
    const handleSortByChange = (e) => {
        onSortChange({ ...currentSort, sortBy: e.target.value });
    };

    const handleSortOrderChange = (e) => {
        onSortChange({ ...currentSort, sortOrder: e.target.value });
    };

    return (
        <div className="sort-controls">
            <div className="sort-group">
                <label htmlFor="sort-by">Сортировать по:</label>
                <select
                    id="sort-by"
                    value={currentSort.sortBy}
                    onChange={handleSortByChange}
                    className="sort-select"
                >
                    <option value="id">По умолчанию</option>
                    <option value="price">Цена</option>
                    <option value="year">Год</option>
                    <option value="manufacturer">Производитель</option>
                </select>
            </div>
            <div className="sort-group">
                <label htmlFor="sort-order">Порядок:</label>
                <select
                    id="sort-order"
                    value={currentSort.sortOrder}
                    onChange={handleSortOrderChange}
                    className="sort-select"
                >
                    <option value="asc">По возрастанию</option>
                    <option value="desc">По убыванию</option>
                </select>
            </div>
        </div>
    );
};

export default SortControls;
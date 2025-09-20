import React, { useState, useEffect } from 'react';
import CarCard from '../components/CarCard';
import Filters from '../components/Filters';
import { carService } from '../services/api';
import './CarList.css';
import SortControls from '../components/SortControls';

const CarList = () => {
  const [cars, setCars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({});
  const [hasMore, setHasMore] = useState(true);
  const [sort, setSort] = useState({ sortBy: 'id', sortOrder: 'asc' });

  useEffect(() => {
    loadCars();
  }, [filters, sort]);

  const loadCars = async (offset = 0) => {
    try {
      setLoading(true);
      const response = await carService.getCars({
        ...filters,
        sort_by: sort.sortBy,
        sort_order: sort.sortOrder,
        offset,
        limit: 20
      });

      console.log('API Response:', response);

      let carsData;
      if (Array.isArray(response)) {
        carsData = response;
      } else if (response && Array.isArray(response.cars)) {
        carsData = response.cars;
      } else if (response && Array.isArray(response.data)) {
        carsData = response.data;
      } else if (response && Array.isArray(response.results)) {
        carsData = response.results;
      } else {
        console.warn('Unexpected API response structure:', response);
        carsData = [];
      }

      console.log('Processed cars data:', carsData);

      if (offset === 0) {
        setCars(carsData);
      } else {
        setCars(prev => [...prev, ...carsData]);
      }

      setHasMore(carsData.length === 20);
      setError(null);
    } catch (err) {
      setError('Не удалось загрузить список автомобилей.');
      console.error('Error loading cars:', err);
      if (offset === 0) {
        setCars([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const loadMore = () => {
    if (!loading && hasMore) {
      loadCars(cars.length);
    }
  };

  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters);
  };

  const handleSortChange = (newSort) => {
    setSort(newSort);
  };

  if (error) {
    return (
      <div className="error-message">
        <p>{error}</p>
        <button onClick={() => loadCars()}>Попробовать снова</button>
      </div>
    );
  }

  return (
    <div className="car-list-page">
      <div className="container">
        <h1>Парсинг Encar</h1>

        <div className="content">
          <aside>
            <Filters
              onFiltersChange={handleFiltersChange}
              currentFilters={filters}
            />
          </aside>

          <main className="main-content">
            <SortControls
              onSortChange={handleSortChange}
              currentSort={sort}
            />

            {loading && cars.length === 0 ? (
              <div className="loading">Загрузка объявлений...</div>
            ) : (
              <>
                <div className="cars-grid">
                  {Array.isArray(cars) && cars.map(car => (
                    <CarCard key={car.id} car={car} />
                  ))}
                </div>

                {(!Array.isArray(cars) || cars.length === 0) && !loading && (
                  <div className="no-results">
                    Нет авто по вашим критериям.
                  </div>
                )}

                {hasMore && Array.isArray(cars) && cars.length > 0 && (
                  <div className="load-more">
                    <button
                      onClick={loadMore}
                      disabled={loading}
                      className="load-more-btn"
                    >
                      {loading ? 'Загрузка...' : 'Показать больше'}
                    </button>
                  </div>
                )}
              </>
            )}
          </main>
        </div>
      </div>
    </div>
  );
};

export default CarList;
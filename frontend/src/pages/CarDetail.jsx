import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { carService } from '../services/api';
import './CarDetail.css';

const CarDetail = () => {
  const { id } = useParams();
  const [car, setCar] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    loadCar();
  }, [id]);

  const loadCar = async () => {
    try {
      setLoading(true);
      const carData = await carService.getCar(id);
      setCar(carData);
      setError(null);
    } catch (err) {
      setError('Failed to load car information.');
      console.error('Error loading car:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price) => {
    if (!price) return 'N/A';
    return `₩${(price * 10000).toLocaleString()}`;
  };

  const formatMileage = (mileage) => {
    if (!mileage) return 'N/A';
    return `${mileage.toLocaleString()} km`;
  };

  const getImageUrl = (photo, type = '001') => {
    if (!photo) return '/placeholder-car.jpg';
    return `https://ci.encar.com/carpicture${photo}${type}.jpg?impolicy=heightRate&rh=696&cw=1160&ch=696&cg=Center`;
  };

  const getImages = () => {
    if (!car?.photos || !Array.isArray(car.photos)) {
      return [getImageUrl(car?.photo)];
    }

    return car.photos.map(photo => getImageUrl(car.photo, photo.type));
  };

  if (loading) {
    return <div className="loading">Загрузка...</div>;
  }

  if (error) {
    return (
      <div className="error-message">
        <p>{error}</p>
        <Link to="/" className="back-link">Обратно к списку</Link>
      </div>
    );
  }

  if (!car) {
    return (
      <div className="error-message">
        <p>Авто не найдено.</p>
        <Link to="/" className="back-link">Обратно к списку</Link>
      </div>
    );
  }

  const images = getImages();

  return (
    <div className="car-detail-page">
      <div className="container">
        <Link to="/" className="back-link">← Обратно к списку</Link>

        <div className="car-detail">
          <div className="car-images">
            <div className="main-image">
              <img
                src={images[currentImageIndex]}
                alt={`${car.manufacturer} ${car.model}`}
                onError={(e) => {
                  e.target.src = '/placeholder-car.jpg';
                }}
              />
            </div>

            {images.length > 1 && (
              <div className="image-thumbnails">
                {images.map((image, index) => (
                  <img
                    key={index}
                    src={image}
                    alt={`${car.manufacturer} ${car.model} ${index + 1}`}
                    className={index === currentImageIndex ? 'active' : ''}
                    onClick={() => setCurrentImageIndex(index)}
                    onError={(e) => {
                      e.target.src = '/placeholder-car.jpg';
                    }}
                  />
                ))}
              </div>
            )}
          </div>

          <div className="car-info">
            <div className="car-header">
              <h1>{car.manufacturer} {car.model}</h1>
              <div className="car-price">{formatPrice(car.price)}</div>
            </div>

            <div className="car-badge-section">
              <h2>{car.badge}</h2>
              {car.badge_detail && <p>{car.badge_detail}</p>}
            </div>

            <div className="info-section">
              <h3>Информация об авто</h3>
              <div className="specs-grid">
                <div className="spec-item">
                  <label>Год</label>
                  <span>{car.form_year || car.year}</span>
                </div>
                <div className="spec-item">
                  <label>Пробег</label>
                  <span>{formatMileage(car.mileage)}</span>
                </div>
                <div className="spec-item">
                  <label>Тип топлива</label>
                  <span>{car.fuel_type}</span>
                </div>
                <div className="spec-item">
                  <label>Трансмиссия</label>
                  <span>{car.transmission}</span>
                </div>
                <div className="spec-item">
                  <label>ID в БД</label>
                  <span>{car.encar_id}</span>
                </div>
                <div className="spec-item">
                  <label>Статус продажи</label>
                  <span>{car.sales_status}</span>
                </div>
              </div>
            </div>

            <div className="info-section">
              <h3>Информация о продавце</h3>
              <div className="dealer-details">
                <div className="dealer-item">
                  <label>Имя продавца</label>
                  <span>{car.dealer_name}</span>
                </div>
                <div className="dealer-item">
                  <label>Компания</label>
                  <span>{car.office_name}</span>
                </div>
                <div className="dealer-item">
                  <label>Город</label>
                  <span>{car.office_city_state}</span>
                </div>
              </div>
            </div>

            {car.service_mark && car.service_mark.length > 0 && (
              <div className="info-section">
                <h3>Проведенное обслуживание</h3>
                <div className="tags">
                  {car.service_mark.map((mark, index) => (
                    <span key={index} className="tag">{mark}</span>
                  ))}
                </div>
              </div>
            )}

            {car.condition && car.condition.length > 0 && (
              <div className="info-section">
                <h3>Состояние авто</h3>
                <div className="tags">
                  {car.condition.map((cond, index) => (
                    <span key={index} className="tag condition">{cond}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CarDetail;
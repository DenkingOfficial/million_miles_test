import React from 'react';
import { Link } from 'react-router-dom';
import './CarCard.css';

const CarCard = ({ car }) => {
  const formatPrice = (price) => {
    if (!price) return 'N/A';
    return `₩${price.toLocaleString()}0,000`;
  };

  const formatMileage = (mileage) => {
    if (!mileage) return 'N/A';
    return `${mileage.toLocaleString()} km`;
  };

  const getImageUrl = (photo) => {
    if (!photo) return '/placeholder-car.jpg';
    return `https://ci.encar.com/carpicture${photo}001.jpg?impolicy=heightRate&rh=696&cw=1160&ch=696&cg=Center`;
  };

  return (
    <div className="car-card">
      <Link to={`/cars/${car.id}`} className="car-card-link">
        <div className="car-image">
          <img 
            src={getImageUrl(car.photo)} 
            alt={`${car.manufacturer} ${car.model}`}
            onError={(e) => {
              e.target.src = '/placeholder-car.jpg';
            }}
          />
        </div>
        <div className="car-info">
          <h3 className="car-title">
            {car.manufacturer} {car.model}
          </h3>
          <p className="car-badge">{car.badge}</p>
          <div className="car-details">
            <span className="car-year">{car.year}</span>
            <span className="car-fuel">{car.fuel_type}</span>
            <span className="car-transmission">{car.transmission}</span>
          </div>
          <div className="car-stats">
            <span className="car-mileage">{formatMileage(car.mileage)}</span>
            <span className="car-location">{car.office_city_state}</span>
          </div>
          <div className="car-price">
            {formatPrice(car.price)}
          </div>
          <div className="car-dealer">
            {car.dealer_name}
          </div>
        </div>
      </Link>
    </div>
  );
};

export default CarCard;

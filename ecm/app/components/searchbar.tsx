import React, { useState } from 'react';
import { getDatabase, ref, child, get } from 'firebase/database';
import { LiftData, Lifts } from '../types';

interface SearchBarProps {
  setLifts: (newLifts: Lifts) => void; // `setLifts` now expects a full `Lifts` object
  onSearchStart: () => void; 
}

const SearchBar: React.FC<SearchBarProps> = ({ setLifts }) => {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string>('');

  const handleSearch = async () => {
    if (searchTerm.trim() === '') {
      setErrorMessage('Please enter a valid location');
      return;
    }

    try {
      const database = getDatabase(); // Get Firebase Database instance
      const dbRef = ref(database); // Create a reference to the database root
      const locationRef = child(dbRef, `cameras`); // Adjust to your Firebase structure

      // Fetch data from Firebase
      const snapshot = await get(locationRef);

      // Log the snapshot to check its structure
      console.log('Snapshot:', snapshot.val());

      const filteredCameras: Partial<Lifts> = {};

      if (snapshot.exists()) {
        snapshot.forEach((childSnapshot) => {
          const data = childSnapshot.val() as LiftData;
          if (data.location.toLowerCase() === searchTerm.toLowerCase()) {
            const cameraKey = childSnapshot.key;
            if (cameraKey) {
              filteredCameras[cameraKey as keyof Lifts] = data;
            }
          }
        });

        if (Object.keys(filteredCameras).length === 0) {
          setErrorMessage('No cameras found for this location');
        } else {
          setErrorMessage(''); // Clear error message if results are found
        }
      } else {
        setErrorMessage('No data available for this search.');
      }

      // Set filtered results directly
      setLifts(filteredCameras as Lifts);
    } catch (error) {
      console.error('Error fetching cameras:', error);
      setErrorMessage('An error occurred while searching.');
    }
  };

  return (
    <div style={{ margin: '20px 0', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <input
        type="text"
        placeholder="Search by location"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        style={{ padding: '10px', width: '300px', border: '1px solid #ccc', borderRadius: '5px' }}
      />
      <button
        onClick={handleSearch}
        style={{ padding: '10px 20px', marginTop: '10px', background: '#007BFF', color: '#fff', border: 'none', borderRadius: '5px' }}
      >
        Search
      </button>
      {errorMessage && <p style={{ color: 'red', marginTop: '10px' }}>{errorMessage}</p>}
    </div>
  );
};

export default SearchBar;

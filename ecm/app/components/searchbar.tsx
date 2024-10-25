import React, { useState } from 'react';
import { getDatabase, ref, child, get } from 'firebase/database';
import { LiftData, Lifts } from '../types';

interface SearchBarProps {
  setLifts: (newLifts: Lifts) => void; // `setLifts` now expects a full `Lifts` object
  onSearchStart: () => void; 
}

const SearchBar: React.FC<SearchBarProps> = ({ setLifts, onSearchStart }) => {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string>('');

  const handleSearch = async () => {
    if (searchTerm.trim() === '') {
      setErrorMessage('Please enter a valid location');
      return;
    }

    onSearchStart(); // Call to indicate search has started
    setErrorMessage(''); // Clear any previous error message

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

  // Handle key press events
  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      handleSearch(); // Trigger search on Enter key press
    }
  };

  return (
    <>
  <input
    type="text"
    placeholder="Search by location"
    value={searchTerm}
    onChange={(e) => setSearchTerm(e.target.value)}
    onKeyDown={handleKeyPress} // Add key press event handler
    className="py-7 w-[70%] text-5xl border-[#E3E3E3] border-[4px] rounded-[20px] px-4 bg-[#00000080] text-white" // Tailwind CSS classes
    />
  {errorMessage && <p className="text-red-500 bg-gray-700 p-2 rounded-md font-bold mt-2">{errorMessage}</p>} {/* Tailwind for error message */}
    </>

  );
};

export default SearchBar;

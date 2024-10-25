"use client"
import { useState, useEffect } from 'react';
import { ref, onValue } from 'firebase/database';
import database from './firebase/firebaseConfig';
import Navbar from './components/navbar';
import { Loader2 } from 'lucide-react'; // Import the Loader2 component
import SearchBar from './components/searchbar';
import { Lifts } from './types';

export default function Home() {
  const [lifts, setLifts] = useState<Lifts | null>(null); // Start with no lifts displayed
  const [loading, setLoading] = useState(false); // Loading state for search

  // Load all cameras initially (only once on mount)
  useEffect(() => {
    setLoading(true);
    const cameraRefs = [
      { id: 'camera1', ref: ref(database, 'cameras/camera1') },
      { id: 'camera2', ref: ref(database, 'cameras/camera2') },
      { id: 'camera3', ref: ref(database, 'cameras/camera3') },
      { id: 'camera4', ref: ref(database, 'cameras/camera4') },
    ];

    cameraRefs.forEach(({ id, ref }) => {
      onValue(ref, (snapshot) => {
        const data = snapshot.val();
        setLifts((prevLifts) => {
          const defaultLiftData = {
            location: 'Unknown location',
            people_count: 'No data',
            crowd_density: 'No data',
            timestamp: 'No data',
          };

          return {
            ...(prevLifts || {}),
            [id]: {
              location: data?.location || defaultLiftData.location,
              people_count: data?.people_count || defaultLiftData.people_count,
              crowd_density: data?.crowd_density || defaultLiftData.crowd_density,
              timestamp: data?.timestamp || defaultLiftData.timestamp,
            },
          } as Lifts;
        });
      });
    });
    setLoading(false);
  }, []); // Empty dependency array ensures it only runs once

  // Triggered when search results are ready
  const handleSearchResults = (newLifts: Lifts) => {
    setLoading(false); // Stop loading when search results are fetched
    setLifts(newLifts); // Replace lifts with search results
  };

  // Triggered when the search begins
  const handleSearchStart = () => {
    setLoading(true); // Start loading
    setLifts(null); // Clear lifts to ensure only search results show up
  };

  const getBorderColor = (crowd_density: string) => {
    if (crowd_density === 'low') {
      return 'border-green-500';
    } else if (crowd_density === 'medium') {
      return 'border-orange-500';
    } else if (crowd_density === 'high') {
      return 'border-red-600';
    } else {
      return 'border-gray-300'; // Default color if no crowd_density data
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center gap-5 bg-[url('/bg.png')]">
      <Navbar />

      {/* Render SearchBar with the necessary props */}
      <SearchBar setLifts={handleSearchResults} onSearchStart={handleSearchStart} />

      {/* Show a loader during search */}
      {loading && (
        <div className="flex justify-center items-center mt-10">
          <Loader2 className="animate-spin" /> {/* Display the Loader2 component */}
        </div>
      )}

      {/* If no lifts are found and not loading */}
      {!loading && lifts === null && (
        <div className="flex justify-center items-center mt-10">
          <Loader2 className="animate-spin" /> {/* Replace the text with Loader2 */}
        </div>
      )}

      {/* Render the camera data if available */}
      {!loading && lifts && Object.keys(lifts).length > 0 && Object.keys(lifts).map((cameraKey) => {
        const camera = lifts[cameraKey as keyof Lifts];
        const borderColor = getBorderColor(camera.crowd_density);

        return (
          <div key={cameraKey} className={`mb-6 w-[70%] p-4 border-[3px] bg-[#000000BF] rounded-lg hover:scale-105 transition-all shadow-lg ${borderColor}`}>
            {/* Use the dynamic camera key as the title */}
            <h2 className="text-xl font-semibold text-white mb-2">{cameraKey.replace('camera', 'Lift ')}</h2>
            <div className="space-y-2 text-white">
              <p className='text-xl'><strong>Location:</strong> <span>{camera.location}</span></p>
              <p><strong>People Count:</strong> <span>{camera.people_count}</span></p>
              <p><strong>Crowd Density:</strong> <span>{camera.crowd_density}</span></p>
              <p><strong>Last Updated:</strong> <span>{camera.timestamp}</span></p>
            </div>
          </div>
        );
      })}
    </div>
  );
}

"use client"
import { useState, useEffect } from 'react';
import { getDatabase, ref, onValue } from 'firebase/database';
import app from "./firebase/firebaseConfig";
const database = getDatabase(app);

type LiftData = {
  location: string;
  people_count: string;
  crowd_density: string;
  timestamp: string;
};

type Lifts = {
  lift1: LiftData;
  lift2: LiftData;
  lift3: LiftData;
  lift4: LiftData;
};

export default function Home() {
  const [lifts, setLifts] = useState({
    lift1: { location: 'Loading...', people_count: 'Loading...', crowd_density: 'Loading...', timestamp: 'Loading...' },
    lift2: { location: 'Loading...', people_count: 'Loading...', crowd_density: 'Loading...', timestamp: 'Loading...' },
    lift3: { location: 'Loading...', people_count: 'Loading...', crowd_density: 'Loading...', timestamp: 'Loading...' },
    lift4: { location: 'Loading...', people_count: 'Loading...', crowd_density: 'Loading...', timestamp: 'Loading...' },
  });

  useEffect(() => {
    const liftRefs = [
      { id: 'lift1', ref: ref(database, 'cameras/camera1') },
      { id: 'lift2', ref: ref(database, 'cameras/camera2') },
      { id: 'lift3', ref: ref(database, 'cameras/camera3') },
      { id: 'lift4', ref: ref(database, 'cameras/camera4') },
    ];

    liftRefs.forEach(({ id, ref }) => {
      onValue(ref, (snapshot) => {
        const data = snapshot.val();
        setLifts((prevLifts) => ({
          ...prevLifts,
          [id]: {
            location: data?.location || 'Unknown location',
            people_count: data?.people_count || 'No data',
            crowd_density: data?.crowd_density || 'No data',
            timestamp: data?.timestamp || 'No data',
          },
        }));
      });
    });
  }, []);

  return (
    <div className="min-h-screen p-4 flex flex-col">
      <h1 className="text-2xl font-bold mb-4">Elevator Crowd Management System </h1>

      {Object.keys(lifts).map((liftKey) => (
        <div key={liftKey} className="mb-6 p-4 border border-gray-300 rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold mb-2">{liftKey.replace('lift', 'Lift ')}</h2>
          <div className="space-y-2">
            <p><strong>Location:</strong> <span>{lifts[liftKey as keyof Lifts].location}</span></p>
            <p><strong>People Count:</strong> <span>{lifts[liftKey as keyof Lifts].people_count}</span></p>
            <p><strong>Crowd Density:</strong> <span>{lifts[liftKey as keyof Lifts].crowd_density}</span></p>
            <p><strong>Last Updated:</strong> <span>{lifts[liftKey as keyof Lifts].timestamp}</span></p>
          </div>
        </div>
      ))}
    </div>
  );
}
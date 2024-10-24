"use client"

export default function Navbar() {
    const handleReload = () => {
        window.location.href = "/";
    };

    return (
        <div className='bg-gray-950 w-full flex mb-10 items-center justify-center py-5'>
            <h1 onClick={handleReload} className="text-2xl hover:scale-105 transition-all font-bold text-center text-white cursor-pointer">
                Elevator Crowd Management System
            </h1>
        </div>
    )
}

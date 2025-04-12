"use client"
import Image from "next/image";
export default function Navbar() {
    const handleReload = () => {
        window.location.href = "/";
    };

    return (
        <div className='bg-gray-950  w-full flex mb-10 items-center group justify-center gap-10  px-32 py-6'>
            <Image alt="bunger" src="/bunger.gif" className="group-hover:scale-105 transition-all" width={100} height={100} />
            <h1 onClick={handleReload} className="text-4xl self-center  hidden lg:block group-hover:scale-105 transition-all  font-bold text-center text-white cursor-pointer">
                Elevator Crowd Management System
            </h1>
        </div>
    )
}

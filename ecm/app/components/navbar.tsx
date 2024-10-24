import Link from "next/link"
export default function Navbar(){
    return(
        <div className='bg-gray-950 w-full flex mb-10 items-center justify-center py-5'>
     <Link href="/"> <h1 className="text-2xl hover:scale-105 transition-all font-bold  text-center text-white">Elevator Crowd Management System</h1> </Link>
      </div>
    )
}
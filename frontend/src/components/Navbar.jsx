import { Ambulance } from 'lucide-react'

function Navbar() {
  return (
    <nav className="border-b border-slate-800
                    bg-slate-950 px-6 py-4">

      <div className="max-w-7xl mx-auto flex items-center gap-3">

        <Ambulance className="text-cyan-400" size={32} />

        <div>
          <h1 className="text-xl font-bold text-white">
            Smart Emergency Corridor
          </h1>

          <p className="text-xs text-slate-400">
            Quantum Enhanced Route Optimization
          </p>
        </div>

      </div>

    </nav>
  )
}

export default Navbar
import { useState, useEffect } from 'react'
import { getBackendStatus } from '../services/api'

import {
  Server,
  Car,
  Atom,
  Route,
  RefreshCw
} from 'lucide-react'

function Home() {
  const [status, setStatus] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const checkStatus = async () => {
    setLoading(true)
    setError('')

    try {
      const data = await getBackendStatus()
      setStatus(data)
    } catch {
      setStatus(null)
      setError('Unable to connect to the Python backend.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkStatus()
  }, [])

  const modules = [
    {
      name: 'FastAPI Backend',
      icon: Server,
      status: status?.backend
    },
    {
      name: 'SUMO Simulation',
      icon: Car,
      status: status?.simulation
    },
    {
      name: 'Quantum VQC',
      icon: Atom,
      status: status?.vqc
    },
    {
      name: 'A* Routing',
      icon: Route,
      status: status?.routing
    }
  ]

  return (
    <main className="max-w-7xl mx-auto px-6 py-16">

      <section className="text-center">

        <p className="text-cyan-400 text-sm tracking-widest uppercase">
          Quantum Machine Learning
        </p>

        <h1 className="mt-4 text-4xl md:text-6xl
                       font-bold text-white">

          Smart Emergency
          <span className="text-cyan-400"> Corridor</span>

        </h1>

        <p className="mt-5 text-slate-400 max-w-2xl mx-auto">
          Congestion-aware emergency route optimization
          using Variational Quantum Classifier and
          A* Search Algorithm.
        </p>

        <button
          onClick={checkStatus}
          disabled={loading}
          className="mt-8 inline-flex items-center gap-2
                     bg-cyan-500 hover:bg-cyan-400
                     text-slate-950 font-semibold
                     px-6 py-3 rounded-lg
                     disabled:opacity-50 cursor-pointer"
        >
          <RefreshCw
            size={18}
            className={loading ? 'animate-spin' : ''}
          />

          {loading ? 'Connecting...' : 'Check System Status'}

        </button>

        {error && (
          <p className="mt-4 text-red-400">
            {error}
          </p>
        )}

      </section>

      <section className="mt-16 grid grid-cols-1
                          sm:grid-cols-2 lg:grid-cols-4 gap-5">

        {modules.map((module) => {
          const Icon = module.icon

          return (
            <div
              key={module.name}
              className="bg-slate-900 border border-slate-800
                         rounded-xl p-6"
            >

              <Icon className="text-cyan-400" size={30} />

              <h2 className="mt-4 font-semibold text-white">
                {module.name}
              </h2>

              <p className={`mt-3 text-sm ${
                module.status === 'Connected'
                  ? 'text-green-400'
                  : 'text-amber-400'
              }`}>

                {loading
                  ? 'Checking...'
                  : module.status || 'Unavailable'}

              </p>

            </div>
          )
        })}

      </section>

    </main>
  )
}

export default Home
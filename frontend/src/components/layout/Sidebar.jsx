import { NavLink } from 'react-router-dom'

export default function Sidebar({ items = [] }) {
  return (
    <aside className="w-56 border-r border-gray-800 py-4 px-3 flex flex-col gap-1 shrink-0">
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            `flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
              isActive
                ? 'bg-indigo-600/20 text-indigo-400 font-medium'
                : 'text-gray-400 hover:text-white hover:bg-gray-800'
            }`
          }
        >
          {item.label}
        </NavLink>
      ))}
    </aside>
  )
}

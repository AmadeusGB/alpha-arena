'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navigation() {
  const pathname = usePathname();

  const navItems = [
    { href: '/', label: '📊 仪表盘' },
    { href: '/insights', label: '📈 资金与风险洞察' },
    { href: '/settings', label: '🎛️ 系统设置' },
  ];

  return (
    <nav className="bg-white dark:bg-zinc-800 border-b border-zinc-200 dark:border-zinc-700">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <Link href="/" className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">
              🧠 Alpha Arena
            </Link>
          </div>
          
          <div className="flex gap-4">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  pathname === item.href
                    ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                    : 'text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-700'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
}


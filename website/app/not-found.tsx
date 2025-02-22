import Header from '@/components/header'
import Link from 'next/link'

export default function NotFound() {
  return (
    <div className='not-found-page'>
      <Header />
      <main className='flex flex-col items-center justify-center min-h-screen px-6 py-12'>
        <div className='max-w-3xl text-center'>
          <h2 className='text-4xl font-bold mb-4'>404 Not Found</h2>
          <Link href="/" className='text-blue-600 hover:underline'>
            Return Home
          </Link>
        </div>
      </main>
    </div>
  )
}

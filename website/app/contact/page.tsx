import Header from "@/components/header";

export default function Home() {
  return (
    <div className="home-page">
      <Header />
      <main className="flex flex-col items-center justify-center min-h-screen px-6 py-12">
        <div className="max-w-3xl text-center">
          <h1 className="text-4xl font-bold mb-6">Project Lead: Steven Yi</h1>
          <h1 className="text-4xl font-bold mb-6">Developer: Andriy Luchko</h1>
        </div>
      </main>
    </div>
  );
}

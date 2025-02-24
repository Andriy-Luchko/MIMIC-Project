import Header from "@/components/header";

export default function Home() {
  return (
    <div className="home-page">
      <Header />
      <main className="flex flex-col items-center justify-center min-h-screen px-6 py-12">
        <div className="max-w-3xl text-center">
          <h1 className="text-4xl font-bold mb-6">Windows Download</h1>
          <p className="text-lg mb-4">
          <a href="/mimicQuery.exe" download>
              Click here to download the Windows app
            </a>
          </p>
          <h1 className="text-4xl font-bold mb-6">MacOS Download</h1>
          <p className="text-lg mb-4">
            <a href="/mimicQuery.zip" download>
              Click here to download the macOS app
            </a>
          </p>
        </div>
      </main>
    </div>
  );
}

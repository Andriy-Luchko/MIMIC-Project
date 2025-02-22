import Header from "@/components/header";

export default function Home() {
  return (
    <div className="home-page">
      <Header />
      <main className="flex flex-col items-center justify-center min-h-screen px-6 py-12">
        <div className="max-w-3xl text-center">
          <h1 className="text-4xl font-bold mb-6">MedData Query</h1>
          <p className="text-lg mb-4">
            This tool provides a user-friendly way to query the <strong>MIMIC-III</strong> clinical database
          </p>
        </div>
      </main>
    </div>
  );
}

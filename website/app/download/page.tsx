'use client';

import { useEffect, useState } from "react";
import Header from "@/components/header";
import { Apple, Monitor } from "lucide-react";

export default function Home() {
  const [windowsUrl, setWindowsUrl] = useState<string | null>(null);
  const [macUrl, setMacUrl] = useState<string | null>(null);
  const [linuxUrl, setLinuxUrl] = useState<string | null>(null);
  const [version, setVersion] = useState<string | null>(null);
  const [preferredOS, setPreferredOS] = useState<'windows' | 'macos' | 'linux' | null>(null);

  useEffect(() => {
    // Detect OS
    const platform = navigator.platform.toLowerCase();
    if (platform.includes("win")) setPreferredOS("windows");
    else if (platform.includes("mac")) setPreferredOS("macos");
    else if (platform.includes("linux")) setPreferredOS("linux");

    // Fetch GitHub release
    async function fetchLatestRelease() {
      const res = await fetch("https://api.github.com/repos/Andriy-Luchko/MIMIC-Project/releases/latest");
      const data = await res.json();

      setVersion(data.tag_name);
      for (const asset of data.assets) {
        const name = asset.name.toLowerCase();
        if (name.includes("windows")) setWindowsUrl(asset.browser_download_url);
        else if (name.includes("macos")) setMacUrl(asset.browser_download_url);
        else if (name.includes("linux")) setLinuxUrl(asset.browser_download_url);
      }
    }

    fetchLatestRelease();
  }, []);

  return (
    <div className="bg-black min-h-screen text-white">
      <Header />
      <main className="flex flex-col items-center justify-center px-6 py-16">
        <div className="max-w-2xl w-full text-center bg-zinc-900 p-10 rounded-2xl shadow-2xl border border-zinc-800">
          <h1 className="text-4xl font-extrabold mb-4 text-white">Download MimicQuery</h1>
          <p className="text-lg mb-10 text-gray-400">
            {version ? `Latest version: ${version}` : 'Loading version...'}
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {/* Windows */}
            <a
              href={windowsUrl || "#"}
              className={`group py-4 px-6 rounded-xl transition flex flex-col items-center font-medium ${
                windowsUrl
                  ? preferredOS === "windows"
                    ? "bg-blue-500 text-black shadow-lg"
                    : "bg-blue-400 hover:bg-blue-500 text-black"
                  : "bg-zinc-700 text-gray-400 cursor-not-allowed"
              }`}
              download
            >
              <Monitor className="w-6 h-6 mb-2" />
              Windows
            </a>

            {/* macOS */}
            <a
              href={macUrl || "#"}
              className={`group py-4 px-6 rounded-xl transition flex flex-col items-center font-medium ${
                macUrl
                  ? preferredOS === "macos"
                    ? "bg-neutral-500 text-black shadow-lg"
                    : "bg-neutral-400 hover:bg-neutral-500 text-black"
                  : "bg-zinc-700 text-gray-400 cursor-not-allowed"
              }`}
              download
            >
              <Apple className="w-6 h-6 mb-2" />
              macOS
            </a>


            {/* Linux */}
            <a
              href={linuxUrl || "#"}
              className={`group py-4 px-6 rounded-xl transition flex flex-col items-center font-medium ${
                linuxUrl
                  ? preferredOS === "linux"
                    ? "bg-green-500 text-black shadow-lg"
                    : "bg-green-400 hover:bg-green-500 text-black"
                  : "bg-zinc-700 text-gray-400 cursor-not-allowed"
              }`}
              download
            >
              <img src="/linux.svg" alt="Linux icon" className="w-6 h-6 mb-2" />
              Linux
            </a>

          </div>

          {/* <p className="mt-8 text-sm text-gray-500">
            Need help? Check our{" "}
            <a href="/docs/install" className="underline hover:text-blue-400">
              install guide
            </a>.
          </p> */}
        </div>
      </main>
    </div>
  );
}

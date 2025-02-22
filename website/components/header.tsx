import Link from "next/link";

const navLinks = [
  { name: "Home", path: "/" },
  { name: "Download", path: "/download" },
  { name: "Contact", path: "/contact" },
  { name: "Source Code", path: "https://github.com/Andriy-Luchko/MIMIC-Project" }, // External link example
];

export default function Header() {
  return (
    <header className="w-full py-4 px-6 border-b">
      <div className="max-w-6xl mx-auto flex justify-between items-center">
        <h1 className="text-2xl font-bold">MedData Query</h1>
        <nav>
          <ul className="flex space-x-4">
            {navLinks.map(({ name, path }) => (
              <li key={name}>
                {path.startsWith("http") ? (
                  <a href={path} target="_blank" rel="noopener noreferrer" className="hover:underline">
                    {name}
                  </a>
                ) : (
                  <Link href={path} className="hover:underline">
                    {name}
                  </Link>
                )}
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </header>
  );
}

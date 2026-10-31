export function NotFoundPage() {
  return <main className="grid min-h-screen place-items-center bg-slate-50 px-5 py-12">
    <section className="max-w-md text-center">
      <p className="eyebrow">ERROR 404</p>
      <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">Page not found</h1>
      <p className="mt-3 text-sm leading-6 text-slate-600">The page you’re looking for doesn’t exist or may have moved.</p>
      <a className="action-button mt-6 inline-flex" href="/">Return to home</a>
    </section>
  </main>
}

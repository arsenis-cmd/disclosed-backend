import Header from '@/components/layout/Header';

export default function ConsidererLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <Header />
      {children}
    </>
  );
}

interface JsonViewerProps {
  data: unknown;
}

export function JsonViewer({ data }: JsonViewerProps) {
  return (
    <pre className="bg-gray-900 text-green-400 text-xs rounded-lg p-4 overflow-auto max-h-64 font-mono">
      {JSON.stringify(data, null, 2)}
    </pre>
  );
}

import { GetServerSidePropsContext } from "next";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { dabblebase } from "@/utils/dabblebase/client";
import { AuthSubject } from "@/client/internal/auth";
import { useState, useRef } from "react";

export default function AuthenticatedPage({
  subject,
}: {
  subject: AuthSubject;
}) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedUrl, setUploadedUrl] = useState<string | null>(null);
  const [fileName, setFileName] = useState("");
  const [isDownloading, setIsDownloading] = useState(false);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [fileList, setFileList] = useState<Array<{
    key: string;
    path: string;
    size: number;
    last_modified: string;
  }> | null>(null);
  const [isListing, setIsListing] = useState(false);
  const [deletingFile, setDeletingFile] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const signOut = async () => {
    dabblebase.auth.signOut({
      continueTo: "/",
    });
  };

  const handleFileUpload = async () => {
    const fileInput = fileInputRef.current;
    if (!fileInput?.files?.[0]) {
      alert("Please select a file first");
      return;
    }

    const file = fileInput.files[0];

    // Check if it's an image
    if (!file.type.startsWith("image/")) {
      alert("Please select an image file");
      return;
    }

    try {
      setIsUploading(true);
      setUploadedUrl(null);

      // Generate a unique filename with timestamp
      const timestamp = Date.now();
      const fileName = `uploads/${timestamp}-${file.name}`;

      const result = await dabblebase.storage.upload({
        file,
        path: fileName,
      });

      setUploadedUrl(result.url);
      alert("File uploaded successfully!");
    } catch (error) {
      console.error("Upload failed:", error);
      alert(
        `Upload failed: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
    } finally {
      setIsUploading(false);
    }
  };

  const handleImageLoad = async () => {
    if (!fileName.trim()) {
      alert("Please enter a filename");
      return;
    }

    try {
      setIsDownloading(true);
      setImageUrl(null);

      // Use the proxy endpoint instead of presigned URL to avoid CORS issues
      const proxyUrl = dabblebase.storage.getUrl(fileName.trim());
      setImageUrl(proxyUrl);
      alert("Image loaded successfully!");
    } catch (error) {
      console.error("Image load failed:", error);
      alert(
        `Failed to load image: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
    } finally {
      setIsDownloading(false);
    }
  };

  const handleListFiles = async () => {
    try {
      setIsListing(true);
      const result = await dabblebase.storage.list();
      setFileList(result.files);
      console.log("Files in storage:", result.files);
    } catch (error) {
      console.error("List files failed:", error);
      alert(
        `Failed to list files: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
    } finally {
      setIsListing(false);
    }
  };

  const handleDeleteFile = async (filePath: string) => {
    if (!confirm(`Are you sure you want to delete "${filePath}"?`)) {
      return;
    }

    try {
      setDeletingFile(filePath);

      await dabblebase.storage.delete({
        path: filePath,
      });

      // Remove the file from the list
      setFileList((prev) =>
        prev ? prev.filter((file) => file.path !== filePath) : null
      );

      // Clear the image if it was the one being displayed
      if (fileName === filePath) {
        setImageUrl(null);
        setFileName("");
      }

      alert("File deleted successfully!");
    } catch (error) {
      console.error("Delete failed:", error);
      alert(
        `Failed to delete file: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
    } finally {
      setDeletingFile(null);
    }
  };

  return (
    <div className="flex flex-col p-8 gap-3 w-full max-w-sm">
      <h1 className="text-lg font-bold">
        Authenticated as User #{subject.id}!
      </h1>

      <div className="flex flex-col gap-2">
        <h2 className="text-md font-semibold">Upload an Image</h2>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="border rounded p-2"
        />
        <Button
          onClick={handleFileUpload}
          disabled={isUploading}
          className="w-full"
        >
          {isUploading ? "Uploading..." : "Upload Image"}
        </Button>

        {uploadedUrl && (
          <div className="mt-2 p-2 bg-green-100 rounded">
            <p className="text-sm text-green-800">
              Image uploaded successfully!
            </p>
            <p className="text-xs text-gray-600 break-all">
              URL: {uploadedUrl}
            </p>
          </div>
        )}
      </div>

      <div className="flex flex-col gap-2">
        <h2 className="text-md font-semibold">Load and Display Image</h2>
        <Input
          type="text"
          placeholder="Enter filename (e.g., uploads/123456-image.jpg)"
          value={fileName}
          onChange={(e) => setFileName(e.target.value)}
          className="w-full"
        />
        <Button
          onClick={handleImageLoad}
          disabled={isDownloading || !fileName.trim()}
          className="w-full"
        >
          {isDownloading ? "Loading..." : "Load Image"}
        </Button>

        {imageUrl && (
          <div className="mt-2 p-2 bg-blue-100 rounded">
            <p className="text-sm text-blue-800 mb-2">
              Image loaded successfully!
            </p>
            <div className="relative w-full" style={{ maxHeight: "300px" }}>
              <Image
                src={imageUrl}
                alt="Downloaded image"
                width={400}
                height={300}
                className="rounded border object-contain"
                style={{ maxHeight: "300px", width: "auto" }}
                onError={() => {
                  alert("Failed to load image. Please check the filename.");
                  setImageUrl(null);
                }}
                unoptimized={true} // Since we're using presigned URLs
              />
            </div>
            <p className="text-xs text-gray-600 break-all mt-2">
              URL: {imageUrl}
            </p>
          </div>
        )}
      </div>

      <div className="flex flex-col gap-2">
        <h2 className="text-md font-semibold">List Files</h2>
        <Button
          onClick={handleListFiles}
          disabled={isListing}
          className="w-full"
        >
          {isListing ? "Loading..." : "List All Files"}
        </Button>

        {fileList && (
          <div className="mt-2 p-2 bg-gray-100 rounded max-h-40 overflow-y-auto">
            <p className="text-sm font-semibold mb-2">
              Files in storage ({fileList.length}):
            </p>
            {fileList.length === 0 ? (
              <p className="text-xs text-gray-600">No files found</p>
            ) : (
              <ul className="text-xs space-y-2">
                {fileList.map((file, index) => (
                  <li key={index} className="border-b pb-2">
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex-1">
                        <div
                          className="font-mono text-blue-600 cursor-pointer hover:underline"
                          onClick={() => setFileName(file.path)}
                        >
                          {file.path}
                        </div>
                        <div className="text-gray-500">
                          Size: {file.size} bytes | Modified:{" "}
                          {new Date(file.last_modified).toLocaleString()}
                        </div>
                      </div>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDeleteFile(file.path)}
                        disabled={deletingFile === file.path}
                        className="text-xs px-2 py-1 h-6"
                      >
                        {deletingFile === file.path ? "..." : "×"}
                      </Button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>

      <div className="flex flex-col gap-2">
        <h2 className="text-md font-semibold">Delete File</h2>
        <Input
          type="text"
          placeholder="Enter filename to delete"
          value={fileName}
          onChange={(e) => setFileName(e.target.value)}
          className="w-full"
        />
        <Button
          onClick={() => handleDeleteFile(fileName.trim())}
          disabled={deletingFile === fileName.trim() || !fileName.trim()}
          variant="destructive"
          className="w-full"
        >
          {deletingFile === fileName.trim() ? "Deleting..." : "Delete File"}
        </Button>
      </div>

      <Button onClick={signOut} variant="outline">
        Sign out
      </Button>
    </div>
  );
}

export async function getServerSideProps(context: GetServerSidePropsContext) {
  // Verify that the user is signed in
  const { subject, error } = dabblebase.auth.verify(
    context.req.cookies["auth-token"]
  );

  if (error || !subject) {
    // If the user is not authenticated, we will redirect the user
    // back to the homepage so the client never recieves anything
    // from the authenticated-only page.
    console.log(error);
    return {
      redirect: {
        destination: "/",
        permanent: false,
      },
    };
  }
  return {
    props: {
      subject: subject,
    },
  };
}

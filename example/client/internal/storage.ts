/** Client containing functionality to interact with Dabblebase Storage */
export type DabblebaseStorageClient = {
  upload(options: { file: File; path: string }): Promise<{ url: string }>;
  uploadDirect(options: { file: File; path: string }): Promise<{ url: string }>;
  download(options: { path: string }): Promise<{ url: string }>;
  getViewUrl(path: string): string;
  list(): Promise<{
    files: Array<{
      key: string;
      path: string;
      size: number;
      last_modified: string;
    }>;
  }>;
  delete(options: { path: string }): Promise<void>;
};

export type StorageClientConfiguration = {
  projectId: string;
  dabblebaseUrl: string;
  projectVerifyKey?: string;
};

export function createStorageClient({
  projectId,
  dabblebaseUrl,
  projectVerifyKey,
}: StorageClientConfiguration): DabblebaseStorageClient {
  // Get headers with project token
  const getAuthHeaders = () => {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    if (projectVerifyKey) {
      headers["X-Project-Token"] = projectVerifyKey;
    }

    return headers;
  };

  return {
    async upload({ file, path }) {
      if (!file) {
        throw new Error("❌ (dabblebase): A file must be provided for upload.");
      }
      if (!path) {
        throw new Error(
          "❌ (dabblebase): A destination path must be provided for upload."
        );
      }

      const encodedPath = encodeURIComponent(path);
      console.log(
        "Making request to:",
        `${dabblebaseUrl}/api/project/${projectId}/storage/upload?path=${encodedPath}`
      );
      console.log("Project token:", projectVerifyKey);

      const presignResponse = await fetch(
        `${dabblebaseUrl}/api/project/${projectId}/storage/upload?path=${encodedPath}`,
        {
          method: "POST",
          headers: getAuthHeaders(),
        }
      );

      if (!presignResponse.ok) {
        const errorText = await presignResponse.text();
        console.error("Upload request failed:", {
          status: presignResponse.status,
          statusText: presignResponse.statusText,
          errorText,
          url: `${dabblebaseUrl}/api/project/${projectId}/storage/upload?path=${encodedPath}`,
          cookies: document.cookie,
        });
        throw new Error(
          `❌ (dabblebase): Failed to request upload URL (${presignResponse.status} ${presignResponse.statusText}). ${errorText}`
        );
      }

      const presignBody: {
        url: string;
        method?: string;
        headers?: Record<string, string>;
      } = await presignResponse.json();

      const uploadResponse = await fetch(presignBody.url, {
        method: presignBody.method ?? "PUT",
        headers: presignBody.headers,
        body: file,
      });

      if (!uploadResponse.ok) {
        throw new Error(
          `❌ (dabblebase): Upload failed (${uploadResponse.status} ${uploadResponse.statusText}).`
        );
      }

      return { url: presignBody.url };
    },
    async uploadDirect({ file, path }) {
      if (!file) {
        throw new Error("❌ (dabblebase): A file must be provided for upload.");
      }
      if (!path) {
        throw new Error(
          "❌ (dabblebase): A destination path must be provided for upload."
        );
      }

      const formData = new FormData();
      formData.append("file", file);

      const encodedPath = encodeURIComponent(path);
      const response = await fetch(
        `${dabblebaseUrl}/api/project/${projectId}/storage/upload-direct?path=${encodedPath}`,
        {
          method: "POST",
          headers: {
            // Don't set Content-Type - let browser set it with boundary for FormData
            "X-Project-Token": projectVerifyKey || "",
          },
          body: formData,
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `❌ (dabblebase): Direct upload failed (${response.status} ${response.statusText}). ${errorText}`
        );
      }

      const result = await response.json();
      // Return the view URL for consistency
      return { url: `${dabblebaseUrl}${result.url}` };
    },
    async download({ path }) {
      if (!path) {
        throw new Error(
          "❌ (dabblebase): A path must be provided for download."
        );
      }

      const encodedPath = encodeURIComponent(path);
      const response = await fetch(
        `${dabblebaseUrl}/api/project/${projectId}/storage/download?path=${encodedPath}`,
        {
          method: "GET",
          headers: getAuthHeaders(),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `❌ (dabblebase): Failed to get download URL (${response.status} ${response.statusText}). ${errorText}`
        );
      }

      const downloadBody: { url: string; method?: string } =
        await response.json();
      return { url: downloadBody.url };
    },
    async list() {
      const response = await fetch(
        `${dabblebaseUrl}/api/project/${projectId}/storage/list`,
        {
          method: "GET",
          headers: getAuthHeaders(),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `❌ (dabblebase): Failed to list files (${response.status} ${response.statusText}). ${errorText}`
        );
      }

      return await response.json();
    },
    getViewUrl(path: string): string {
      if (!path) {
        throw new Error(
          "❌ (dabblebase): A path must be provided for view URL."
        );
      }

      // Encode the path for URL safety
      const encodedPath = path
        .split("/")
        .map((segment) => encodeURIComponent(segment))
        .join("/");
      return `${dabblebaseUrl}/api/project/${projectId}/storage/view/${encodedPath}?X-Project-Token=${encodeURIComponent(
        projectVerifyKey || ""
      )}`;
    },
    async delete({ path }) {
      if (!path) {
        throw new Error(
          "❌ (dabblebase): A destination path must be provided for deletion."
        );
      }

      const encodedPath = encodeURIComponent(path);
      const response = await fetch(
        `${dabblebaseUrl}/api/project/${projectId}/storage/delete?path=${encodedPath}`,
        {
          method: "DELETE",
          headers: getAuthHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error(
          `❌ (dabblebase): Failed to delete the file (${response.status} ${response.statusText}).`
        );
      }
    },
  };
}

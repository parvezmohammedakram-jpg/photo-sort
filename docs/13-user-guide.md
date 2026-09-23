# PhotoSort User Guide

Welcome to PhotoSort! This guide will help you navigate the system and use it to automatically evaluate, categorize, and organize your photo collections.

## 1. Getting Started

When you open PhotoSort in your browser (typically at `http://localhost:5173`), you will start on the **Dashboard** or **Import** screen.

### Importing Photos
1. Navigate to the **Import** view using the sidebar navigation.
2. In the "Local Directory Path" field, type the full, absolute path to the folder on your computer containing the images you want to analyze (e.g., `C:\Users\YourName\Pictures\Wedding`).
3. (Optional) Provide a custom "Project Name".
4. Click **Start Processing**.

> [!NOTE]
> PhotoSort **safely reads** your photos. It will **never** modify, move, or delete your original source files.

## 2. Processing

After you start an import, you will be redirected to the **Processing** view.
Here you can see the real-time progress of your photos as they go through the Analysis Engine.

The engine evaluates:
- **Focus/Sharpness**: Detecting motion blur or out-of-focus subjects.
- **Exposure**: Identifying severely under or overexposed shots.
- **Faces & Eyes**: Finding closed eyes.
- **Duplicates**: Grouping identical or visually similar images.

You do not need to stay on this screen while processing happens—it runs in the background.

## 3. Reviewing Results

Once processing is complete, use the **Results** and **Dashboard** tabs to review your photos.

### Dashboard
The Dashboard gives you a high-level summary:
- Total photos processed.
- Breakdown of categories (Good, Review, Poor).
- Number of blurry, improperly exposed, or duplicate photos found.

### Results Grid
Navigate to the **Results** tab to browse your photos:
- **Filtering**: Use the category buttons at the top to view only "Good", "Review", or "Poor" photos.
- **Pagination**: Use the Previous/Next buttons at the bottom to navigate large collections.
- **Details**: Click on any photo to open the **Photo Detail View**.

### Photo Detail View & Manual Overrides
Clicking on a photo shows you exactly *why* PhotoSort gave it a specific score.
- You can review the exact metrics for Blur, Exposure, and Faces.
- If you disagree with the automated categorization, you can **manually override** it by clicking one of the Category buttons (Good, Review, Poor). Your manual decision will be permanently saved.

## 4. Handling Duplicates

Navigate to the **Duplicates** tab to view grouped photos.
- PhotoSort groups photos that are either mathematically identical (exact copies) or visually similar (burst shots, slight angle changes).
- These groups are displayed side-by-side so you can easily compare them and decide which ones to keep.

## 5. Exporting Your Selections

Once you are satisfied with the categorizations, you can export your preferred photos.
1. Navigate to the **Export** tab.
2. Enter a **Destination Folder Path** (e.g., `C:\Exports\Wedding_Final`).
3. Select the categories you want to export. For example, you might only want to export "Good" photos.
4. Click **Start Export**.

PhotoSort will *copy* the selected photos into the destination folder. Your original files will remain untouched in their original location.

---
> [!TIP]
> If you process a very large directory (1,000+ images), allow the background processor time to complete. You can monitor the progress bar, but closing the browser window will *not* stop the backend from working!

/**
 * File Parser Utilities
 * Extracts headers from CSV and Excel files
 */

/**
 * Parse CSV file and extract headers
 */
export async function parseCSVHeaders(file: File): Promise<string[]> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const lines = content.split('\n');
        if (lines.length === 0) {
          reject(new Error('CSV file is empty'));
          return;
        }
        
        // Get first line and parse headers
        const headerLine = lines[0];
        const headers = parseCSVLine(headerLine);
        
        if (headers.length === 0) {
          reject(new Error('No headers found in CSV file'));
          return;
        }
        
        resolve(headers);
      } catch (error) {
        reject(error);
      }
    };
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsText(file);
  });
}

/**
 * Parse a single CSV line, handling quoted values
 */
function parseCSVLine(line: string): string[] {
  const result: string[] = [];
  let current = '';
  let insideQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];

    if (char === '"') {
      insideQuotes = !insideQuotes;
    } else if (char === ',' && !insideQuotes) {
      result.push(current.trim().replace(/^"|"$/g, ''));
      current = '';
    } else {
      current += char;
    }
  }

  if (current) {
    result.push(current.trim().replace(/^"|"$/g, ''));
  }

  return result;
}

/**
 * Parse Excel file and extract headers
 * Requires xlsx library
 */
export async function parseExcelHeaders(file: File): Promise<string[]> {
  try {
    // Dynamically import xlsx to reduce bundle size if not used
    const XLSX = await import('xlsx').then(mod => mod.default || mod);

    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = e.target?.result as ArrayBuffer;
          const workbook = XLSX.read(data, { type: 'array' });
          
          if (workbook.SheetNames.length === 0) {
            reject(new Error('Excel file has no sheets'));
            return;
          }

          // Read first sheet
          const sheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[sheetName];
          
          // Get headers from first row
          const headers: string[] = [];
          let col = 0;
          
          while (true) {
            const cellRef = XLSX.utils.encode_col(col) + '1';
            const cell = worksheet[cellRef];
            
            if (!cell || cell.v === undefined) {
              break;
            }
            
            headers.push(String(cell.v).trim());
            col++;
          }

          if (headers.length === 0) {
            reject(new Error('No headers found in Excel file'));
            return;
          }

          resolve(headers);
        } catch (error) {
          reject(error);
        }
      };
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsArrayBuffer(file);
    });
  } catch (error) {
    throw new Error('Excel library (xlsx) is required to parse Excel files. Please ensure it is installed.');
  }
}

/**
 * Extract headers from any supported file type
 */
export async function extractFileHeaders(file: File): Promise<string[]> {
  const fileName = file.name.toLowerCase();
  
  if (fileName.endsWith('.csv')) {
    return parseCSVHeaders(file);
  } else if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
    return parseExcelHeaders(file);
  } else {
    throw new Error(`Unsupported file type: ${file.name}. Supported: CSV, XLSX, XLS`);
  }
}

/**
 * Smart column mapping suggestion
 * Attempts to match file columns to expected columns
 */
export function suggestColumnMapping(
  fileColumns: string[],
  requiredColumns: string[]
): Record<string, string | null> {
  const mapping: Record<string, string | null> = {};
  const usedFileColumns = new Set<string>();

  // Initialize all required columns as null
  requiredColumns.forEach((col) => {
    mapping[col] = null;
  });

  // Create lowercase mapping of file columns for fuzzy matching
  const fileColumnsLower = fileColumns.map((col) => ({
    original: col,
    lower: col.toLowerCase(),
  }));

  // Define keywords for each required column
  const keywordMap: Record<string, string[]> = {
    Date: ['date', 'transaction date', 'txn date', 'posting date', 'value date', 'trans_date'],
    Narration: ['narration', 'description', 'remarks', 'details', 'memo', 'transaction desc', 'comment'],
    'Withdrawal Amt.': ['withdrawal', 'debit', 'withdraw', 'out', 'payment', 'expense', 'debit amt'],
    'Deposit Amt.': ['deposit', 'credit', 'deposit amount', 'credit amount', 'income', 'in', 'credit amt'],
  };

  // Try to match each required column
  requiredColumns.forEach((requiredCol) => {
    const keywords = keywordMap[requiredCol] || [];

    for (const fileCol of fileColumnsLower) {
      if (usedFileColumns.has(fileCol.original)) {
        continue; // Skip already mapped columns
      }

      // Check if any keyword matches
      const matches = keywords.some((keyword) => fileCol.lower.includes(keyword) || keyword.includes(fileCol.lower));

      if (matches) {
        mapping[requiredCol] = fileCol.original;
        usedFileColumns.add(fileCol.original);
        break; // Move to next required column
      }
    }
  });

  return mapping;
}

import { stringify } from 'csv-stringify/sync';
import ExcelJS from 'exceljs';

export const exportCSV = async (data: Record<string, any>[], columns: string[]): Promise<Buffer> => {
  const csvString = stringify(data, {
    header: true,
    columns: columns
  });
  return Buffer.from(csvString);
};

export const exportXLSX = async (data: Record<string, any>[], columns: string[], sheetName: string): Promise<Buffer> => {
  const workbook = new ExcelJS.Workbook();
  const worksheet = workbook.addWorksheet(sheetName);
  
  worksheet.columns = columns.map(col => ({ header: col, key: col }));
  worksheet.addRows(data);
  
  const buffer = await workbook.xlsx.writeBuffer();
  return Buffer.from(buffer as ArrayBuffer);
};

export const success = (data: any, message?: string) => {
  return {
    success: true,
    data,
    ...(message && { message })
  };
};

export const error = (message: string, statusCode = 500) => {
  return {
    success: false,
    error: message,
    statusCode
  };
};

export const paginated = (data: any[], total: number, page: number, limit: number) => {
  return {
    success: true,
    data,
    meta: {
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit)
    }
  };
};

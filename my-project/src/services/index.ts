import { fetchData } from './fetchData';
import { processData } from './processData';

export const getData = async () => {
    const data = await fetchData();
    return processData(data);
};

export const someOtherService = () => {
    // Implementation of another service function
};
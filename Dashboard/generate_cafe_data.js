import fetch from 'node-fetch';
import { parse } from 'csv-parse/sync';
import { stringify } from 'csv-stringify/sync';
import fs from 'fs';

// Fetch menu data
async function getMenuData() {
    const menuResponse = await fetch('https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Cafe_Menu-sm46Uw6wyFqxL84PKGycYVkdLSGDuL.csv');
    const menuData = await menuResponse.text();
    return parse(menuData, { columns: true, skip_empty_lines: true });
}

// Asynchronous function to generate the dataset
async function generateDatasetAsync(numTransactions) {
    const menuItems = await getMenuData();

    // Organize menu items by category
    const menuByCategory = menuItems.reduce((acc, item) => {
        if (!acc[item.Category]) {
            acc[item.Category] = [];
        }
        acc[item.Category].push({ name: item.Item, price: parseFloat(item['Price (INR)']) });
        return acc;
    }, {});

    const startDate = new Date('2023-01-01');
    const endDate = new Date('2023-12-31');
    const paymentMethods = ['Card', 'Cash', 'UPI', 'Mobile Wallet'];
    const transactions = [];

    for (let i = 1; i <= numTransactions; i++) {
        const date = randomDate(startDate, endDate);
        const orderDetails = generateOrderItems(menuByCategory);

        transactions.push({
            'Transaction ID': i.toString(),
            'Date': date.toISOString().split('T')[0],
            'Time': randomTime(),
            'Items Purchased': orderDetails.items,
            'Quantities': orderDetails.quantities,
            'Total Price (INR)': orderDetails.totalPrice,
            'Payment Method': paymentMethods[Math.floor(Math.random() * paymentMethods.length)]
        });
    }

    return transactions;
}


// Helper functions
const randomDate = (start, end) => {
    return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
};

const randomTime = () => {
    const hours = Math.floor(Math.random() * (21 - 8) + 8); // 8 AM to 9 PM
    const minutes = Math.floor(Math.random() * 60);
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
};

const generateOrderItems = (menuByCategory) => {
    const numItems = Math.floor(Math.random() * 3) + 1; // 1 to 3 items per order
    const items = [];
    const quantities = [];
    let totalPrice = 0;

    // Get available categories
    const availableCategories = Object.keys(menuByCategory).filter(cat => cat !== 'Add-Ons');

    // Add main items
    for (let i = 0; i < numItems; i++) {
        const category = availableCategories[Math.floor(Math.random() * availableCategories.length)];
        if (menuByCategory[category] && menuByCategory[category].length > 0) {
            const item = menuByCategory[category][Math.floor(Math.random() * menuByCategory[category].length)];
            const quantity = Math.floor(Math.random() * 2) + 1; // 1 or 2 quantities
            items.push(item.name);
            quantities.push(quantity);
            totalPrice += item.price * quantity;
        }
    }

    // Randomly add add-ons
    if (Math.random() > 0.5 && menuByCategory['Add-Ons'] && menuByCategory['Add-Ons'].length > 0) {
        const addOn = menuByCategory['Add-Ons'][Math.floor(Math.random() * menuByCategory['Add-Ons'].length)];
        items.push(addOn.name);
        quantities.push(1);
        totalPrice += addOn.price;
    }

    return {
        items: items.join(', '),
        quantities: quantities.join(', '),
        totalPrice: parseFloat(totalPrice.toFixed(2))
    };
};

// Main execution block
async function main() {
    // Generate 10000 transactions
    const dataset = await generateDatasetAsync(10000);

    // Convert to CSV
    const csvContent = stringify(dataset, { header: true });

    // Write to file
    fs.writeFileSync('cafe_transactions.csv', csvContent);

    console.log("Dataset generated successfully. Sample of first 5 transactions:");
    console.log(dataset.slice(0, 5));

    console.log("\nDataset statistics:");
    console.log(`Total transactions: ${dataset.length}`);
    console.log(`Date range: ${dataset[0].Date} to ${dataset[dataset.length - 1].Date}`);

    // Calculate total revenue
    const totalRevenue = dataset.reduce((sum, transaction) => sum + transaction['Total Price (INR)'], 0);
    console.log(`Total revenue: ₹${totalRevenue.toLocaleString()}`);

    // Calculate average transaction value
    console.log(`Average transaction value: ₹${(totalRevenue / dataset.length).toFixed(2)}`);

    // Most popular item
    const itemCounts = dataset.reduce((acc, transaction) => {
        transaction['Items Purchased'].split(', ').forEach(item => {
            acc[item] = (acc[item] || 0) + 1;
        });
        return acc;
    }, {});
    const mostPopularItem = Object.entries(itemCounts).reduce((a, b) => a[1] > b[1] ? a : b);
    console.log(`Most popular item: ${mostPopularItem[0]} (${mostPopularItem[1]} times)`);

    // Most used payment method
    const paymentMethodCounts = dataset.reduce((acc, transaction) => {
        acc[transaction['Payment Method']] = (acc[transaction['Payment Method']] || 0) + 1;
        return acc;
    }, {});
    const mostUsedPaymentMethod = Object.entries(paymentMethodCounts).reduce((a, b) => a[1] > b[1] ? a : b);
    console.log(`Most used payment method: ${mostUsedPaymentMethod[0]} (${mostUsedPaymentMethod[1]} times)`);
}


main();



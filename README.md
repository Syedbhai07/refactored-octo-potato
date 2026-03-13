# Bhai

A Dynamics 365 Business Central AL extension demonstrating best practices for descriptive variable and function naming.

## Naming Conventions

This project follows these AL naming guidelines to keep code readable and self-documenting:

### Variables

| Instead of | Use |
|---|---|
| `c` | `customerRecord` |
| `sl` | `salesLine` |
| `n` | `salesOrderNumber` |
| `tot` | `totalOrderAmount` |
| `qty` | `quantityToOrder` |
| `flag` | `orderPostedSuccessfully` |

### Functions / Procedures

| Instead of | Use |
|---|---|
| `Create()` | `CreateSalesOrderForCustomer()` |
| `Calc()` | `CalculateOrderTotalAmount()` |
| `Check()` | `IsCustomerEligibleForDiscount()` |
| `Post()` | `PostApprovedSalesOrder()` |

### Guidelines

- **Variables** should clearly describe what data they hold, including the record type when applicable (e.g. `salesHeader`, `customerRecord`).
- **Procedures** should start with a verb and describe the action and subject (e.g. `CalculateOrderTotalAmount`, `CreateSalesOrderForCustomer`).
- **Boolean variables** should read as a statement (e.g. `orderPostedSuccessfully`, `isCustomerEligibleForDiscount`).
- **Parameters** should describe the expected value, not just the data type (e.g. `customerNumber` instead of `custNo` or `c`).

## Example

See [`SalesOrderManagement.Codeunit.al`](./SalesOrderManagement.Codeunit.al) for a practical example of these conventions applied to sales order processing logic.
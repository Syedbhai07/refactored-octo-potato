codeunit 50100 "Sales Order Management"
{
    // Demonstrates descriptive variable and function naming conventions for AL development.

    procedure CreateSalesOrderForCustomer(customerNumber: Code[20]; itemNumber: Code[20]; quantityToOrder: Decimal): Code[20]
    var
        salesHeader: Record "Sales Header";
        salesLine: Record "Sales Line";
        newSalesOrderNumber: Code[20];
    begin
        // Create sales header for the specified customer
        salesHeader.Init();
        salesHeader."Document Type" := salesHeader."Document Type"::Order;
        salesHeader."Sell-to Customer No." := customerNumber;
        salesHeader.Insert(true);
        newSalesOrderNumber := salesHeader."No.";

        // Add a sales line for the requested item and quantity
        salesLine.Init();
        salesLine."Document Type" := salesHeader."Document Type";
        salesLine."Document No." := newSalesOrderNumber;
        salesLine."Line No." := 10000;
        salesLine.Type := salesLine.Type::Item;
        salesLine."No." := itemNumber;
        salesLine.Quantity := quantityToOrder;
        salesLine.Insert(true);

        exit(newSalesOrderNumber);
    end;

    procedure CalculateOrderTotalAmount(salesOrderNumber: Code[20]): Decimal
    var
        salesLine: Record "Sales Line";
        totalOrderAmount: Decimal;
    begin
        totalOrderAmount := 0;

        salesLine.SetRange("Document Type", salesLine."Document Type"::Order);
        salesLine.SetRange("Document No.", salesOrderNumber);
        if salesLine.FindSet() then
            repeat
                totalOrderAmount += salesLine."Line Amount";
            until salesLine.Next() = 0;

        exit(totalOrderAmount);
    end;

    procedure IsCustomerEligibleForDiscount(customerNumber: Code[20]; currentOrderAmount: Decimal; minimumOrderAmount: Decimal): Boolean
    var
        customerRecord: Record Customer;
        customerCreditLimit: Decimal;
        customerBalanceDue: Decimal;
    begin
        if not customerRecord.Get(customerNumber) then
            exit(false);

        customerCreditLimit := customerRecord."Credit Limit (LCY)";
        customerBalanceDue := customerRecord."Balance Due (LCY)";

        // Customer is eligible if their balance due is below the credit limit
        // and the current order amount meets or exceeds the minimum threshold
        exit((customerBalanceDue < customerCreditLimit) and (currentOrderAmount >= minimumOrderAmount));
    end;

    procedure PostApprovedSalesOrder(salesOrderNumber: Code[20]): Boolean
    var
        salesHeader: Record "Sales Header";
        salesPostProcedure: Codeunit "Sales-Post";
        orderPostedSuccessfully: Boolean;
    begin
        if not salesHeader.Get(salesHeader."Document Type"::Order, salesOrderNumber) then
            exit(false);

        if salesHeader.Status <> salesHeader.Status::Released then
            exit(false);

        salesPostProcedure.Run(salesHeader);
        orderPostedSuccessfully := true;

        exit(orderPostedSuccessfully);
    end;
}

import {
    List,
    Frame,
    Toast,
    DataTable,
    DatePicker,
    Checkbox,
    Select,
    AppProvider,
    Card,
    TextField,
    Button,
    TextStyle,
    EmptyState,
    Form,
    FormLayout,
    Layout,
    Page
} from '@shopify/polaris';
import React, {Component, useState, useCallback} from 'react';
import ReactDOM from "react-dom";
import '@shopify/polaris/build/esm/styles.css';

import translations from '@shopify/polaris/locales/en.json';

const AppConfig = window.config;

class AccountSettingForm extends Component {
    constructor(props) {
        super(props);
        this.state = {
            current_sale_account: AppConfig.shopify_store.sale_account,
            current_shipping_account: AppConfig.shopify_store.shipping_account,
            current_payment_account: AppConfig.shopify_store.payment_account,
            current_auto_sync: ((AppConfig.shopify_store.auto_sync == 1) ? true : false),
            sale_account_options: AppConfig.sale_accounts.map((account) => (
                {label: account.name, value: account.code}
            )),
            shipping_account_options: AppConfig.shipping_accounts.map((account) => (
                {label: account.name, value: account.code}
            )),
            payment_account_options: AppConfig.payment_accounts.map((account) => (
                {label: account.name, value: account.code}
            )),
        };
        this.handleSaleAccountSelectChange = this.handleSaleAccountSelectChange.bind(this);
        this.handleShippingAccountSelectChange = this.handleShippingAccountSelectChange.bind(this);
        this.handlePaymentAccountSelectChange = this.handlePaymentAccountSelectChange.bind(this);
        this.handleAutoSyncChange = this.handleAutoSyncChange.bind(this);
    };

    handleSaleAccountSelectChange(value) {
        this.setState({current_sale_account: value});
    };

    handleShippingAccountSelectChange(value) {
        this.setState({current_shipping_account: value});
    };

    handlePaymentAccountSelectChange(value) {
        this.setState({current_payment_account: value});
    };

    handleAutoSyncChange(value) {
        this.setState({current_auto_sync: value});
    };

    SaveSettingUrl() {
        var current_sale_account = this.state.current_sale_account
        var current_shipping_account = this.state.current_shipping_account
        var current_payment_account = this.state.current_payment_account
        var current_auto_sync = ''
        if (this.state.current_auto_sync == true) {
            current_auto_sync = 'True'
        }
        let url = '/save_settings?sale_account=' + current_sale_account + '&shipping_account=' + current_shipping_account + '&payment_account=' + current_payment_account + '&auto_sync=' + current_auto_sync
        return url
    }

    render() {
        return (
            <Form>
                <FormLayout>
                    <Select name="sale_account" label="Sales Account" options={this.state.sale_account_options}
                            onChange={this.handleSaleAccountSelectChange}
                            value={this.state.current_sale_account}/>
                    <Select name="shipping_account" label="Shipping Account"
                            options={this.state.shipping_account_options}
                            onChange={this.handleShippingAccountSelectChange}
                            value={this.state.current_shipping_account}/>
                    <Select name="payment_account"
                            label='Payment Account (Account with "Enable payments to this account" enabled):'
                            options={this.state.payment_account_options}
                            onChange={this.handlePaymentAccountSelectChange}
                            value={this.state.current_payment_account}/>
                    <Checkbox name="auto_sync" label="Automatically Sync (at midnight everyday)"
                              checked={this.state.current_auto_sync}
                              onChange={this.handleAutoSyncChange}/>
                    <Button onClick={event => location.href = this.SaveSettingUrl()} primary>Save Settings</Button>
                </FormLayout>
            </Form>
        )
    };
}

class ExportForm extends Component {
    constructor(props) {
        super(props);
        var newDate = new Date();
        if (AppConfig.shopify_store.timezone) {
            newDate = new Date(newDate.toLocaleString('en-US', {timeZone: AppConfig.shopify_store.timezone}));
        }
        this.state = {
            timezone: AppConfig.shopify_store.timezone,
            date: {month: newDate.getMonth(), year: newDate.getFullYear()},
            selectedDate: {start: newDate, end: newDate},

        };
        this.handleSelectedDates = this.handleSelectedDates.bind(this);
        this.handleMonthChange = this.handleMonthChange.bind(this);
    }

    handleSelectedDates(value) {
        this.setState({selectedDate: value})
    }

    handleMonthChange(value) {
        this.setState({date: value})
    }

    SyncToXeroUrl() {
        let from_date = new Date(this.state.selectedDate.start)
        let to_date = new Date(this.state.selectedDate.end)
        from_date = $.datepicker.formatDate('mm/dd/yy', from_date);
        to_date = $.datepicker.formatDate('mm/dd/yy', to_date);
        let url = '/sync_to_xero?from_date=' + from_date + '&to_date=' + to_date
        return url

    }

    render() {
        return (
            <Form>
                <DatePicker
                    month={this.state.date.month}
                    year={this.state.date.year}
                    onChange={this.handleSelectedDates}
                    onMonthChange={this.handleMonthChange}
                    selected={this.state.selectedDate}
                    multiMonth
                    allowRange
                />
                <br/>
                <Button onClick={event => location.href = this.SyncToXeroUrl()} primary>Export Data</Button>
            </Form>
        );
    }
}

class HistoryTable extends Component {

    constructor(props) {
        super(props);
        this.state = {
            logs: AppConfig.logs,
            orders_synced: AppConfig.shopify_store.orders_synced,
            store_plan_order_number: AppConfig.shopify_store.store_plan_order_number,
        };
    }

    showPlanOrderNumber() {
        if (this.state.store_plan_order_number > 0) {
            return this.state.store_plan_order_number
        } else {
            return 'Unlimited'
        }
    }

    render() {
        return (
            <Page>
                <Card>
                    <Card.Section>
                        <p>History log of sync history, including automated jobs.</p>
                        <p>Orders synced this month: {this.state.orders_synced}</p>
                        <p>Current Orders per plan: {this.showPlanOrderNumber()}</p>
                    </Card.Section>
                    <DataTable
                        columnContentTypes={[
                            'datetime',
                            'datetime',
                            'text',
                            'text',
                        ]}
                        headings={[
                            'Excution Time',
                            'Finish Time',
                            'Status',
                            'Message',
                        ]}
                        rows={this.state.logs}
                    />
                </Card>
            </Page>
        );
    }
}


class Main extends Component {

    constructor(props) {
        super(props);
        this.state = {
            message: AppConfig.message,
        };
        this.toggleActive = this.toggleActive.bind(this);
    }

    toggleActive() {
        this.setState({message: null})
    }

    render() {
        let message;
        if (this.state.message) {
            message = <Toast content={this.state.message} onDismiss={this.toggleActive}/>
        }
        return (
            <AppProvider i18n={translations}>
                <Frame>
                    {message}
                    <Page title="General Settings">
                        <Layout>
                            <Layout.AnnotatedSection
                                description={
                                    <p>
                                        Please choose your account accordingly: <br/>
                                        - Sales Account will be applied to Invoice Line Items' Account<br/>
                                        - Shipping Account will be applied to Shipping as an Invoice Line Item<br/>
                                        - Payments will go to Payment Account on Xero
                                    </p>
                                }
                            >
                                <AccountSettingForm/>
                            </Layout.AnnotatedSection>
                        </Layout>
                    </Page>
                    <Page title="Export To Xero">
                        <Layout>
                            <Layout.AnnotatedSection
                                description={
                                    <p>
                                        - Choose date from and date to and export your data to Xero.<br/>
                                    </p>
                                }>
                                <ExportForm/>
                            </Layout.AnnotatedSection>
                        </Layout>
                    </Page>
                    <Page title="History">
                        <Layout>
                            <Layout.Section>
                                <HistoryTable/>
                            </Layout.Section>
                        </Layout>
                    </Page>
                </Frame>
            </AppProvider>
        )
    }
}

export default Main;


if (typeof document != "undefined") {
    const wrapper = document.getElementById("xero_main_render");
    wrapper ? ReactDOM.render(<Main/>, wrapper) : false;
}



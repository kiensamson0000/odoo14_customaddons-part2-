import "./style.css"
import {Link, Thumbnail, Button, MediaCard, Frame, FormLayout, Layout, Page, AppProvider} from '@shopify/polaris';
import React, {Component} from 'react';
import ReactDOM from "react-dom";

import '@shopify/polaris/build/esm/styles.css'
import translations from '@shopify/polaris/locales/en.json';
import image from './maxresdefault.jpg';

class Main extends Component {

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <AppProvider i18n={translations}>
                <Frame>
                    <Page>
                        <div className="content1">
                            <div>
                                <img className="img1" src={image} alt="Connect to Xero" width="640px" height="360px"/>
                            </div>
                            <div className="div1">
                                <Button onClick={event => window.top.location.href = "/shopify/auth/<string:name>"}
                                        primary>Connect To Xero</Button>
                            </div>
                        </div>

                        <div className="content2">
                            <b>Welcome to Xero Integration</b>
                            <ol>
                                <li><Link onClick={event => window.top.location.href = "https://www.xero.com/signup/"}>Signup
                                    an account xero</Link> if you haven't already
                                </li>
                                <li>Click "Connect to Xero"</li>
                                <li>Login to Xero if you haven't already</li>
                                <li>Click "Accept" to start connecting to the application</li>
                                <li>Start Exporting data to your Xero Account</li>
                                <li>Thank you!</li>
                            </ol>
                        </div>
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

//
//  ViewController.h
//  RasPiRemote
//
//  Created by Will Frank on 02/12/2017.
//  Copyright (c) 2017 Will Frank. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface ViewController : UIViewController <NSStreamDelegate> {
    BOOL _connectInProgress;
    
    NSOutputStream *_outputStream;
}

@property(nonatomic, strong) IBOutlet UITextField *host;
@property(nonatomic, strong) IBOutlet UITextField *port;
@property(nonatomic, strong) IBOutlet UIButton *connect;
@property(nonatomic, strong) IBOutlet UIButton *disconnect;
@property(nonatomic, strong) IBOutlet UILabel *status;

- (IBAction)doConnect:(id)sender;
- (IBAction)doDisconnect:(id)sender;

- (IBAction)turnLeft:(id)sender;
- (IBAction)turnRight:(id)sender;

- (IBAction)stop:(id)sender;

@end

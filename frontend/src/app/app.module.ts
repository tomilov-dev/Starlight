import { APP_INITIALIZER, NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ComponentsModule } from './components/components.module';
import { HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { PagesModule } from './pages/pages.module';
import { FormsModule } from '@angular/forms';
import { SvgModule } from './svg/svg.module';
import { ApiService } from './services/api.service';
import { DataService } from './services/data.service';

export function initializeApp(
  apiService: ApiService,
  dataService: DataService
) {
  return (): Promise<void> => {
    return new Promise((resolve, reject) => {
      apiService.getGenres().subscribe({
        next: (genres) => {
          dataService.setGenres(genres);
          apiService.getCountries().subscribe({
            next: (countries) => {
              dataService.setCountries(countries);
              resolve();
            },
            error: (err) => reject(err),
          });
        },
        error: (err) => reject(err),
      });
    });
  };
}

@NgModule({
  declarations: [AppComponent],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    CommonModule,
    // my modules
    ComponentsModule,
    PagesModule,
    FormsModule,
    SvgModule,
  ],
  providers: [
    ApiService,
    DataService,
    {
      provide: APP_INITIALIZER,
      useFactory: initializeApp,
      deps: [ApiService, DataService],
      multi: true,
    },
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}

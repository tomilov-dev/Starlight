import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HeaderComponent } from './header/header.component';
import { FooterComponent } from './footer/footer.component';
import { RouterModule } from '@angular/router';
import { ItemMovieComponent } from './item-movie/item-movie.component';
import { ItemPersonComponent } from './item-person/item-person.component';
import { SvgModule } from '../svg/svg.module';

@NgModule({
  declarations: [
    HeaderComponent,
    FooterComponent,
    ItemMovieComponent,
    ItemPersonComponent,
  ],
  imports: [CommonModule, RouterModule, SvgModule],
  exports: [
    HeaderComponent,
    FooterComponent,
    ItemMovieComponent,
    ItemPersonComponent,
  ],
})
export class ComponentsModule {}
